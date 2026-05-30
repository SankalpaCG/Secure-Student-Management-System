from datetime import datetime

from flask import current_app, g, request

from app.api import api_bp
from app.api.decorators import roles_required
from app.api.errors import json_error
from app.api.schemas import EnrollSchema
from app.api.serializers import attendance_json, enrollment_json, grade_json
from app.extensions import db, limiter
from app.models.course import Course
from app.models.enums import EnrollmentStatus
from app.models.enrollment import Enrollment
from app.services.audit_service import log_event
from app.student import services as student_svc


@api_bp.route("/student/enrollments", methods=["GET"])
@roles_required("Student")
def api_student_enrollments():
    enrollments = student_svc.active_enrollments(g.api_user.id)
    return {"enrollments": [enrollment_json(e) for e in enrollments]}


@api_bp.route("/student/grades", methods=["GET"])
@roles_required("Student")
def api_student_grades():
    grades = student_svc.all_grades(g.api_user.id)
    log_event(g.api_user.id, "VIEW_GRADES", target_type="student", severity="INFO")
    return {"grades": [grade_json(gr) for gr in grades]}


@api_bp.route("/student/attendance", methods=["GET"])
@roles_required("Student")
def api_student_attendance():
    records = student_svc.all_attendance(g.api_user.id)
    log_event(g.api_user.id, "VIEW_ATTENDANCE", target_type="student", severity="INFO")
    return {"attendance": [attendance_json(r) for r in records]}


@api_bp.route("/student/enroll", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("ENROLLMENT_RATE_LIMIT", "20 per hour"))
@roles_required("Student")
def api_student_enroll():
    try:
        data = EnrollSchema().load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    course_id = data["course_id"]
    student_id = g.api_user.id
    course = db.session.get(Course, course_id)
    if not course or not course.is_active:
        return json_error("Course not found or not available.", 404, code="not_found")

    if course_id in student_svc.enrolled_course_ids(student_id):
        return json_error("Already enrolled in this course.", 409, code="already_enrolled")

    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        existing.status = EnrollmentStatus.ACTIVE
        existing.enrolled_at = datetime.utcnow()
        db.session.commit()
        log_event(student_id, "ENROLL_COURSE", target_type="enrollment", target_id=existing.id)
        return {"enrollment": enrollment_json(existing)}, 200

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        status=EnrollmentStatus.ACTIVE,
        enrolled_at=datetime.utcnow(),
    )
    db.session.add(enrollment)
    db.session.commit()
    log_event(
        student_id,
        "ENROLL_COURSE",
        target_type="enrollment",
        target_id=enrollment.id,
        details={"course_id": course_id},
    )
    return {"enrollment": enrollment_json(enrollment)}, 201
