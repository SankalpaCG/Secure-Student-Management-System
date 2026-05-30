from flask import render_template
from flask_login import current_user

from app.admin import admin_bp
from app.admin.services import get_dashboard_data
from app.utils.decorators import admin_required


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    data = get_dashboard_data()
    return render_template(
        "admin/dashboard.html",
        admin_name=current_user.full_name,
        breadcrumb_title="Dashboard",
        **data,
    )
