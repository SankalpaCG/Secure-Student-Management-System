from flask import current_app, g, request

from app.api import api_bp
from app.api.decorators import roles_required
from app.api.errors import json_error
from app.api.schemas import CreateGradeSchema, MarkAttendanceSchema, UpdateGradeSchema
from app.api.serializers import course_summary, grade_json
from app.extensions import db, limiter
from app.models.enums import AttendanceStatus
from app.models.grade import Grade
from app.services.audit_service import log_event
from app.teacher import services as teacher_svc
from app.utils import access_control as ac
from app.utils.sanitize import sanitize_text


@api_bp.route("/teacher/courses", methods=["GET"])
@roles_required("Teacher")
def api_teacher_courses():
    courses = teacher_svc.assigned_courses(g.api_user.id)
    return {"courses": [course_summary(c) for c in courses]}


@api_bp.route("/teacher/course/<int:course_id>/students", methods=["GET"])
@roles_required("Teacher")
def api_teacher_course_students(course_id):
    course = ac.require_teacher_course(g.api_user.id, course_id)
    rows = teacher_svc.course_student_rows(course.id)
    students = []
    for row in rows:
        s = row["student"]
        students.append({
            "id": s.id,
            "full_name": s.full_name,
            "email": s.email,
            "student_number": row["student_number"],
            "attendance_pct": row["attendance_pct"],
            "avg_grade": row["avg_grade"],
        })
    return {"course": course_summary(course), "students": students}


@api_bp.route("/teacher/grades", methods=["POST"])
@limiter.limit("30 per hour")
@roles_required("Teacher")
def api_teacher_create_grade():
    try:
        data = CreateGradeSchema().load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    teacher_id = g.api_user.id
    course = ac.require_teacher_course(teacher_id, data["course_id"])
    if not ac.check_student_enrolled(data["student_id"], course.id):
        return json_error("Student is not enrolled in this course.", 400, code="not_enrolled")

    grade = Grade(
        student_id=data["student_id"],
        course_id=course.id,
        teacher_id=teacher_id,
        assessment_name=sanitize_text(data["assessment_name"], 100),
        grade_value=str(data["grade_value"]),
        feedback=sanitize_text(data.get("feedback") or "", 2000) or None,
    )
    db.session.add(grade)
    db.session.commit()
    log_event(teacher_id, "CREATE_GRADE", target_type="grade", target_id=grade.id)
    return {"grade": grade_json(grade)}, 201


@api_bp.route("/teacher/grades/<int:grade_id>", methods=["PUT"])
@limiter.limit("30 per hour")
@roles_required("Teacher")
def api_teacher_update_grade(grade_id):
    try:
        data = UpdateGradeSchema().load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    grade = ac.require_teacher_grade(g.api_user.id, grade_id)
    grade.grade_value = str(data["grade_value"])
    grade.feedback = sanitize_text(data.get("feedback") or "", 2000) or None
    grade.teacher_id = g.api_user.id
    db.session.commit()
    log_event(g.api_user.id, "UPDATE_GRADE", target_type="grade", target_id=grade.id)
    return {"grade": grade_json(grade)}


@api_bp.route("/teacher/attendance", methods=["POST"])
@limiter.limit("60 per hour")
@roles_required("Teacher")
def api_teacher_mark_attendance():
    try:
        data = MarkAttendanceSchema().load(request.get_json(silent=True) or {})
    except Exception as err:
        from marshmallow import ValidationError

        if isinstance(err, ValidationError):
            return json_error("Validation failed.", 422, "validation_error", err.messages)
        raise

    teacher_id = g.api_user.id
    course = ac.require_teacher_course(teacher_id, data["course_id"])
    entries = []
    for entry in data["entries"]:
        if not ac.check_student_enrolled(entry["student_id"], course.id):
            continue
        try:
            AttendanceStatus(entry["status"])
        except ValueError:
            return json_error(
                f"Invalid attendance status: {entry['status']}",
                422,
                code="validation_error",
            )
        remarks = entry.get("remarks")
        entries.append({
            "student_id": entry["student_id"],
            "status": entry["status"],
            "remarks": sanitize_text(remarks, 500) if remarks else None,
        })

    count = teacher_svc.save_attendance_grid(
        teacher_id, course.id, data["attendance_date"], entries
    )
    db.session.commit()
    log_event(
        teacher_id,
        "MARK_ATTENDANCE",
        target_type="course",
        target_id=course.id,
        details={"date": data["attendance_date"].isoformat(), "count": count},
    )
    return {
        "saved_count": count,
        "course_id": course.id,
        "attendance_date": data["attendance_date"].isoformat(),
    }
