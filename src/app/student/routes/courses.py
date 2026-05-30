from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.models.course import Course
from app.models.enums import EnrollmentStatus
from app.models.enrollment import Enrollment
from app.student import student_bp
from app.student import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import student_required


@student_bp.route("/courses")
@student_required
def courses():
    available = svc.available_courses(current_user.id)
    return render_template(
        "student/courses.html",
        courses=available,
        breadcrumb_title="Available Courses",
    )


@student_bp.route("/courses/<int:course_id>/enroll", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("ENROLLMENT_RATE_LIMIT", "20 per hour"))
@student_required
def enroll(course_id):
    course = db.session.get(Course, course_id)
    if not course or not course.is_active:
        flash("Course not found or not available.", "danger")
        return redirect(url_for("student.courses"))

    if course.id in svc.enrolled_course_ids(current_user.id):
        flash("You are already enrolled in this course.", "info")
        return redirect(url_for("student.enrollments"))

    if request.method == "POST":
        existing = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course.id,
        ).first()

        if existing:
            if existing.status == EnrollmentStatus.ACTIVE:
                flash("You are already enrolled in this course.", "info")
            else:
                existing.status = EnrollmentStatus.ACTIVE
                existing.enrolled_at = datetime.utcnow()
                db.session.commit()
                log_event(current_user.id, "ENROLL_COURSE", target_type="enrollment", target_id=existing.id)
                flash(f"Re-enrolled in {course.course_name}.", "success")
            return redirect(url_for("student.enrollments"))

        enrollment = Enrollment(
            student_id=current_user.id,
            course_id=course.id,
            status=EnrollmentStatus.ACTIVE,
            enrolled_at=datetime.utcnow(),
        )
        db.session.add(enrollment)
        db.session.commit()
        log_event(
            current_user.id,
            "ENROLL_COURSE",
            target_type="enrollment",
            target_id=enrollment.id,
            details={"course_id": course.id},
        )
        flash(f"Successfully enrolled in {course.course_name}.", "success")
        return redirect(url_for("student.enrollments"))

    return render_template(
        "student/enroll.html",
        course=course,
        breadcrumb_title=f"Enroll — {course.course_code}",
    )
