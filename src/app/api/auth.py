from flask import current_app, request

from app.api import api_bp
from app.api.errors import json_error
from app.api.schemas import LoginSchema, LogoutSchema, RefreshSchema
from app.api.serializers import profile_summary
from app.extensions import db, limiter
from app.models.user import User
from app.services.audit_service import log_event
from app.services.jwt_service import (
    JWTError,
    create_token_pair,
    decode_token,
    get_user_from_payload,
    revoke_token,
)
from app.utils.security import verify_password
from app.utils.totp import verify_totp_code


@api_bp.route("/auth/login", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("API_LOGIN_RATE_LIMIT", "10 per minute"))
def api_login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.is_active or not verify_password(
        user.password_hash, data["password"]
    ):
        log_event(
            user_id=user.id if user else None,
            action="API_LOGIN_FAILED",
            target_type="auth",
            severity="HIGH",
            details={"email": email},
        )
        return json_error("Invalid email or password.", 401, code="invalid_credentials")

    if user.is_2fa_enabled:
        totp_code = (data.get("totp_code") or "").strip()
        if not totp_code:
            return json_error(
                "Two-factor authentication code is required.",
                401,
                code="totp_required",
            )
        if not verify_totp_code(user.totp_secret, totp_code):
            log_event(
                user_id=user.id,
                action="TWO_FA_FAILED",
                target_type="user",
                target_id=user.id,
                severity="HIGH",
                details={"channel": "api"},
            )
            return json_error("Invalid two-factor code.", 401, code="invalid_totp")

    access_token, refresh_token = create_token_pair(user)
    log_event(
        user_id=user.id,
        action="API_LOGIN_SUCCESS",
        target_type="auth",
        severity="INFO",
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "role": user.role.value,
        "profile": profile_summary(user),
    }


@api_bp.route("/auth/refresh", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("API_REFRESH_RATE_LIMIT", "30 per minute"))
def api_refresh():
    schema = RefreshSchema()
    try:
        data = schema.load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    try:
        payload = decode_token(data["refresh_token"], expected_type="refresh")
        user = get_user_from_payload(payload)
    except JWTError as exc:
        return json_error(exc.message, 401, code=exc.code)

    from app.services.jwt_service import create_access_token

    access_token = create_access_token(user)
    log_event(user_id=user.id, action="API_TOKEN_REFRESH", target_type="auth", severity="INFO")
    return {"access_token": access_token, "token_type": "Bearer"}


@api_bp.route("/auth/logout", methods=["POST"])
@limiter.limit("30 per minute")
def api_logout():
    schema = LogoutSchema()
    try:
        data = schema.load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    revoked_any = False
    user_id = None

    try:
        refresh_payload = decode_token(data["refresh_token"], expected_type="refresh")
        user_id = refresh_payload.get("sub")
        if revoke_token(refresh_payload["jti"]):
            revoked_any = True
    except JWTError:
        pass

    access_token = data.get("access_token") or _bearer_from_header()
    if access_token:
        try:
            access_payload = decode_token(access_token, expected_type="access")
            user_id = user_id or access_payload.get("sub")
            if revoke_token(access_payload["jti"]):
                revoked_any = True
        except JWTError:
            pass

    if revoked_any:
        log_event(
            user_id=int(user_id) if user_id else None,
            action="JWT_REVOKED",
            target_type="auth",
            severity="MEDIUM",
        )
        return {"message": "Logged out successfully."}

    return json_error("No valid token to revoke.", 400, code="logout_failed")


def _bearer_from_header():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None
