from flask import render_template
from flask_login import current_user
from sqlalchemy.orm import joinedload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.student import student_bp
from app.utils.decorators import student_required


@student_bp.route("/enrollments")
@student_required
def enrollments():
    records = (
        Enrollment.query.filter_by(student_id=current_user.id)
        .options(joinedload(Enrollment.course).joinedload(Course.teacher))
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )
    return render_template(
        "student/enrollments.html",
        enrollments=records,
        breadcrumb_title="My Enrollments",
    )
