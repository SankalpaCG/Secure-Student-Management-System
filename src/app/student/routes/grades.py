from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.extensions import db
from app.models.grade import Grade
from app.student import student_bp
from app.student import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import student_required
from app.utils.permissions import ensure_student_resource


@student_bp.route("/grades")
@student_required
def grades():
    log_event(current_user.id, "VIEW_GRADES", target_type="student", target_id=current_user.id)
    all_grades = svc.all_grades(current_user.id)
    trend = svc.grade_trend(current_user.id, limit=20)
    return render_template(
        "student/grades.html",
        grades=all_grades,
        grade_trend=trend,
        breadcrumb_title="My Grades",
    )


@student_bp.route("/grades/<int:grade_id>")
@student_required
def grade_detail(grade_id):
    grade = db.session.get(Grade, grade_id)
    if not grade:
        flash("Grade not found.", "danger")
        return redirect(url_for("student.grades"))
    ensure_student_resource(current_user.id, grade.student_id)
    return render_template(
        "student/grade_detail.html",
        grade=grade,
        breadcrumb_title="Grade Detail",
    )
