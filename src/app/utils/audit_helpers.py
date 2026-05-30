"""Audit severity display helpers for templates and dashboards."""

SEVERITY_BADGE = {
    "CRITICAL": "danger",
    "HIGH": "warning",
    "MEDIUM": "primary",
    "LOW": "secondary",
    "INFO": "info",
    # Legacy lowercase mappings
    "critical": "danger",
    "high": "warning",
    "medium": "primary",
    "low": "secondary",
    "info": "info",
}


def get_action_severity(action, stored_severity=None):
    """Return severity for display; prefer value stored on the audit row."""
    if stored_severity:
        return stored_severity.upper()
    from app.services.audit_service import _ACTION_DEFAULT_SEVERITY

    return _ACTION_DEFAULT_SEVERITY.get(str(action).upper(), "LOW")
