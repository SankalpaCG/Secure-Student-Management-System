"""JWT issuance, validation, and revocation."""

import uuid
from datetime import datetime, timezone

import jwt
from flask import current_app

from app.extensions import db
from app.models.revoked_token import RevokedToken
from app.models.user import User


class JWTError(Exception):
    """Base JWT validation error."""

    def __init__(self, message, code="invalid_token"):
        self.message = message
        self.code = code
        super().__init__(message)


def _utcnow():
    return datetime.now(timezone.utc)


def _encode(payload, expires_delta):
    now = _utcnow()
    payload = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def _role_value(user):
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def create_access_token(user):
    """Issue a new short-lived access token."""
    return _encode(
        {
            "sub": str(user.id),
            "role": _role_value(user),
            "jti": str(uuid.uuid4()),
            "type": "access",
        },
        current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    )


def create_refresh_token(user):
    """Issue a new long-lived refresh token."""
    return _encode(
        {
            "sub": str(user.id),
            "role": _role_value(user),
            "jti": str(uuid.uuid4()),
            "type": "refresh",
        },
        current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
    )


def create_token_pair(user):
    """Return (access_token, refresh_token)."""
    return create_access_token(user), create_refresh_token(user)


def decode_token(token, expected_type=None):
    if not token:
        raise JWTError("Token is required.", "missing_token")
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        raise JWTError("Token has expired.", "token_expired")
    except jwt.InvalidTokenError:
        raise JWTError("Invalid token.", "invalid_token")

    if expected_type and payload.get("type") != expected_type:
        raise JWTError("Invalid token type.", "invalid_token_type")

    jti = payload.get("jti")
    if not jti:
        raise JWTError("Token missing jti claim.", "invalid_token")

    if is_token_revoked(jti):
        raise JWTError("Token has been revoked.", "token_revoked")

    return payload


def is_token_revoked(jti):
    return RevokedToken.query.filter_by(jti=jti).first() is not None


def revoke_token(jti):
    if not jti or is_token_revoked(jti):
        return False
    db.session.add(RevokedToken(jti=jti))
    db.session.commit()
    return True


def get_user_from_payload(payload):
    user_id = payload.get("sub")
    if user_id is None:
        raise JWTError("Token missing subject.", "invalid_token")
    user = db.session.get(User, int(user_id))
    if not user or not user.is_active:
        raise JWTError("User not found or inactive.", "user_inactive")
    return user
