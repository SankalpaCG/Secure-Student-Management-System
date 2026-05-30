"""
Centralized audit logging service.

All security-relevant events should be recorded via log_event().
Never log passwords, tokens, TOTP secrets, or other sensitive plaintext.
"""

import json
import logging
from datetime import datetime

from flask import has_request_context, request
from flask_login import current_user

from app.extensions import db
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

# Keys stripped from details payloads (case-insensitive substring match).
_SENSITIVE_DETAIL_KEYS = frozenset({
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "totp",
    "secret",
    "recovery_code",
    "backup_code",
    "authorization",
    "csrf",
})

# Default severity when not supplied explicitly.
_ACTION_DEFAULT_SEVERITY = {
  # Authentication
    "LOGIN_SUCCESS": "INFO",
    "LOGIN_FAILED": "HIGH",
    "LOGOUT": "INFO",
    "TWO_FA_SETUP": "MEDIUM",
    "TWO_FA_SUCCESS": "INFO",
    "TWO_FA_FAILED": "HIGH",
    "TWO_FA_RESET": "HIGH",
    # Access control
    "UNAUTHORIZED_ACCESS": "CRITICAL",
    "FORBIDDEN_ROUTE": "HIGH",
    "IDOR_ATTEMPT": "CRITICAL",
    # Admin
    "CREATE_USER": "MEDIUM",
    "UPDATE_USER": "LOW",
    "DEACTIVATE_USER": "HIGH",
    "ASSIGN_ROLE": "MEDIUM",
    "RESET_USER_2FA": "HIGH",
    "CREATE_COURSE": "LOW",
    "UPDATE_COURSE": "LOW",
    "ASSIGN_TEACHER": "MEDIUM",
    "EXPORT_AUDIT_LOGS": "MEDIUM",
    "EXPORT_USERS": "MEDIUM",
    # Teacher
    "CREATE_GRADE": "LOW",
    "UPDATE_GRADE": "LOW",
    "MARK_ATTENDANCE": "LOW",
    "UPDATE_TEACHER_PROFILE": "LOW",
    # Student
    "UPDATE_STUDENT_PROFILE": "LOW",
    "ENROLL_COURSE": "LOW",
    "VIEW_GRADES": "INFO",
    "VIEW_ATTENDANCE": "INFO",
    # API (reserved for future JWT routes)
    "API_LOGIN_SUCCESS": "INFO",
    "API_LOGIN_FAILED": "HIGH",
    "API_TOKEN_REFRESH": "INFO",
    "API_VIEW_AUDIT_LOGS": "INFO",
    "JWT_REVOKED": "MEDIUM",
    "JWT_ACCESS_DENIED": "HIGH",
    # Security
    "RATE_LIMIT_TRIGGERED": "HIGH",
    "SUSPICIOUS_ACTIVITY": "CRITICAL",
    "VIEW_SECURITY_DASHBOARD": "INFO",
}


def _normalize_severity(severity, action):
    if severity:
        return str(severity).upper()
    return _ACTION_DEFAULT_SEVERITY.get(action, "LOW")


def _sanitize_details(details):
    """Return JSON string safe for storage, with sensitive keys removed."""
    if details is None:
        return None
    if isinstance(details, str):
        text = details.strip()
        return text[:4000] if text else None
    if not isinstance(details, dict):
        try:
            details = {"value": str(details)}
        except Exception:
            return None
    clean = {}
    for key, value in details.items():
        key_lower = str(key).lower()
        if any(s in key_lower for s in _SENSITIVE_DETAIL_KEYS):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean[key] = value
        else:
            clean[key] = str(value)[:500]
    if not clean:
        return None
    try:
        return json.dumps(clean)[:4000]
    except (TypeError, ValueError):
        return None


def _request_meta():
    if not has_request_context():
        return None, None
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    ua = request.user_agent.string[:255] if request.user_agent else None
    return ip, ua


def log_event(
    user_id,
    action,
    target_type=None,
    target_id=None,
    severity="INFO",
    details=None,
):
    """
    Record an audit event. Failures are logged but never propagate to callers.

    Args:
        user_id: Acting user id, or None for anonymous/system events.
        action: Stable action code (e.g. LOGIN_SUCCESS).
        target_type: Resource type (user, course, grade, ...).
        target_id: Resource primary key when applicable.
        severity: INFO | LOW | MEDIUM | HIGH | CRITICAL
        details: Optional dict or string with non-sensitive context.
    """
    try:
        if user_id is None and current_user and current_user.is_authenticated:
            user_id = current_user.id

        action = str(action).upper()
        sev = _normalize_severity(severity, action)
        ip_address, user_agent = _request_meta()
        details_json = _sanitize_details(details)

        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type or "system",
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=sev,
            details=details_json,
            timestamp=datetime.utcnow(),
        )

        with db.session.begin_nested():
            db.session.add(entry)
            db.session.flush()
    except Exception:
        logger.exception("Audit log failed for action=%s", action)


def log_idor_attempt(target_type, target_id=None, details=None):
    """Log an insecure direct object reference attempt before aborting."""
    uid = current_user.id if current_user.is_authenticated else None
    payload = dict(details or {})
    if has_request_context():
        payload.setdefault("endpoint", request.endpoint)
        payload.setdefault("path", request.path)
    log_event(
        user_id=uid,
        action="IDOR_ATTEMPT",
        target_type=target_type,
        target_id=target_id,
        severity="CRITICAL",
        details=payload,
    )


def log_forbidden_route(required_roles=None):
    """Log access to a route forbidden for the current role."""
    uid = current_user.id if current_user.is_authenticated else None
    log_event(
        user_id=uid,
        action="FORBIDDEN_ROUTE",
        target_type="route",
        severity="HIGH",
        details={
            "endpoint": request.endpoint if has_request_context() else None,
            "path": request.path if has_request_context() else None,
            "user_role": current_user.role.value if current_user.is_authenticated else None,
            "required_roles": required_roles,
        },
    )
