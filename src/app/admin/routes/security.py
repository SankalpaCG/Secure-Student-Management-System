from flask import redirect, render_template, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.admin.security_services import get_security_dashboard_data
from app.services.audit_service import log_event
from app.utils.decorators import admin_required


@admin_bp.route("/security-dashboard")
@admin_required
def security_dashboard():
    log_event(
        user_id=current_user.id,
        action="VIEW_SECURITY_DASHBOARD",
        target_type="admin",
        severity="INFO",
    )
    data = get_security_dashboard_data()
    return render_template(
        "admin/security_dashboard.html",
        breadcrumb_title="Security Dashboard",
        **data,
    )


@admin_bp.route("/security")
@admin_required
def security_dashboard_legacy():
    """Legacy URL redirect."""
    return redirect(url_for("admin.security_dashboard"))
