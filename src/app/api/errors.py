"""Consistent JSON error responses for the API."""

from flask import jsonify
from marshmallow import ValidationError

from app.services.jwt_service import JWTError
from app.utils.access_control import AccessDenied, ResourceNotFound


def json_error(message, status=400, code=None, details=None):
    body = {"error": message}
    if code:
        body["code"] = code
    if details is not None:
        body["details"] = details
    return jsonify(body), status


def register_api_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        if _is_api_request():
            return json_error(
                "Validation failed.",
                422,
                code="validation_error",
                details=err.messages,
            )
        raise err

    @app.errorhandler(JWTError)
    def handle_jwt(err):
        if _is_api_request():
            return json_error(err.message, 401, code=err.code)
        raise err

    @app.errorhandler(AccessDenied)
    def handle_access_denied(err):
        if _is_api_request():
            from app.services.audit_service import log_event
            from flask import g

            api_user = getattr(g, "api_user", None)
            log_event(
                user_id=api_user.id if api_user else None,
                action="JWT_ACCESS_DENIED",
                target_type=err.target_type,
                target_id=err.target_id,
                severity="HIGH",
                details=err.details,
            )
            return json_error("Access denied.", 403, code="access_denied")
        raise err

    @app.errorhandler(ResourceNotFound)
    def handle_not_found(err):
        if _is_api_request():
            return json_error(
                f"{err.resource_type} not found.",
                404,
                code="not_found",
            )
        raise err


def _is_api_request():
    from flask import request

    return request.path.startswith("/api/")
