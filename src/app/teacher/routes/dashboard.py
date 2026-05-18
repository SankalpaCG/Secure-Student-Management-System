from flask import render_template
from flask_login import current_user

from app.teacher import teacher_bp
from app.teacher import services as svc
from app.utils.decorators import teacher_required


@teacher_bp.route("/dashboard")
@teacher_required
def dashboard():
    data = svc.get_dashboard_data(current_user.id, current_user.full_name)
    return render_template(
        "teacher/dashboard.html",
        breadcrumb_title="Dashboard",
        **data,
    )
