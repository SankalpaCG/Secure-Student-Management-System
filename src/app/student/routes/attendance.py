from flask import render_template
from flask_login import current_user

from app.student import student_bp
from app.student import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import student_required


@student_bp.route("/attendance")
@student_required
def attendance():
    log_event(current_user.id, "VIEW_ATTENDANCE", target_type="student", target_id=current_user.id)
    records = svc.all_attendance(current_user.id)
    course_chart = svc.attendance_by_course(current_user.id)
    overall_pct = svc.overall_attendance_pct(current_user.id)
    return render_template(
        "student/attendance.html",
        records=records,
        course_chart=course_chart,
        overall_pct=overall_pct,
        breadcrumb_title="My Attendance",
    )
