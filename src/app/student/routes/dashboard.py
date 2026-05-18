from flask import render_template
from flask_login import current_user

from app.student import student_bp
from app.student import services as svc
from app.utils.decorators import student_required


@student_bp.route("/dashboard")
@student_required
def dashboard():
    data = svc.get_dashboard_data(current_user)
    return render_template(
        "student/dashboard.html",
        breadcrumb_title="Dashboard",
        **data,
    )
