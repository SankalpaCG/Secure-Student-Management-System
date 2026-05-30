from flask import g, request

from app.admin import services as admin_svc
from app.admin.security_services import get_security_dashboard_data
from app.api import api_bp
from app.api.decorators import roles_required
from app.api.serializers import audit_log_json, user_public
from app.services.audit_service import log_event


@api_bp.route("/admin/users", methods=["GET"])
@roles_required("Admin")
def api_admin_users():
    search = request.args.get("search")
    role = request.args.get("role")
    status = request.args.get("status")
    limit = min(request.args.get("limit", 50, type=int), 100)
    users = admin_svc.users_query(search=search, role=role, status=status).limit(limit).all()
    return {"users": [user_public(u) for u in users]}


@api_bp.route("/admin/audit-logs", methods=["GET"])
@roles_required("Admin")
def api_admin_audit_logs():
    action = request.args.get("action")
    user_id = request.args.get("user_id", type=int)
    severity = request.args.get("severity")
    limit = min(request.args.get("limit", 50, type=int), 100)
    logs = (
        admin_svc.audit_logs_query(action=action, user_id=user_id, severity=severity)
        .limit(limit)
        .all()
    )
    log_event(g.api_user.id, "API_VIEW_AUDIT_LOGS", target_type="admin", severity="INFO")
    return {"audit_logs": [audit_log_json(log) for log in logs]}


@api_bp.route("/admin/security-summary", methods=["GET"])
@roles_required("Admin")
def api_admin_security_summary():
    data = get_security_dashboard_data()
    log_event(
        g.api_user.id,
        action="VIEW_SECURITY_DASHBOARD",
        target_type="admin",
        severity="INFO",
        details={"channel": "api"},
    )
    return {
        "summary": {
            "failed_logins_24h": data["failed_logins_24h"],
            "failed_2fa_24h": data["failed_2fa_24h"],
            "unauthorized_24h": data["unauthorized_24h"],
            "rate_limit_24h": data["rate_limit_24h"],
            "high_severity_24h": data["high_severity_24h"],
            "active_users": data["active_users"],
            "risk_score": data["risk_score"],
        },
        "suspicious_ip_count": len(data["suspicious_ips"]),
        "recent_high_risk_count": len(data["recent_high_risk"]),
        "generated_at": data["generated_at"].isoformat(),
    }
