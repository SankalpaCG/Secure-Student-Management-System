"""Backward-compatible audit helper — prefer app.services.audit_service.log_event."""

from app.services.audit_service import log_event


def log_audit(action, target_type="system", target_id=None, user_id=None, severity=None, details=None):
    """Record a security-relevant event (delegates to log_event)."""
    log_event(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        severity=severity or "INFO",
        details=details,
    )
