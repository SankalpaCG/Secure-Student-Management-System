"""JWT authentication and RBAC decorators for API routes."""

from functools import wraps

from flask import g, request

from app.api.errors import json_error
from app.models.enums import UserRole
from app.services.audit_service import log_event
from app.services.jwt_service import JWTError, decode_token, get_user_from_payload


def _extract_bearer_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_bearer_token()
        if not token:
            return json_error("Authorization header required.", 401, code="missing_token")
        try:
            payload = decode_token(token, expected_type="access")
            user = get_user_from_payload(payload)
        except JWTError as exc:
            log_event(
                user_id=None,
                action="JWT_ACCESS_DENIED",
                target_type="api",
                severity="HIGH",
                details={"reason": exc.code},
            )
            return json_error(exc.message, 401, code=exc.code)

        g.api_user = user
        g.token_payload = payload
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required
        def wrapper(*args, **kwargs):
            allowed = {r if isinstance(r, UserRole) else UserRole(r) for r in roles}
            if g.api_user.role not in allowed:
                log_event(
                    user_id=g.api_user.id,
                    action="FORBIDDEN_ROUTE",
                    target_type="api",
                    severity="HIGH",
                    details={
                        "required_roles": [r.value for r in allowed],
                        "path": request.path,
                    },
                )
                return json_error("Insufficient permissions.", 403, code="forbidden")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
