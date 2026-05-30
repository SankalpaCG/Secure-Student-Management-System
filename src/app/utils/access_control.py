"""Shared access-control primitives for web and API routes."""

from app.extensions import db
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import EnrollmentStatus
from app.models.grade import Grade
from app.services.audit_service import log_idor_attempt


class AccessDenied(Exception):
    """Raised when a user attempts to access a resource they do not own."""

    def __init__(self, target_type, target_id, details=None):
        self.target_type = target_type
        self.target_id = target_id
        self.details = details or {}
        super().__init__(f"Access denied to {target_type}:{target_id}")


class ResourceNotFound(Exception):
    """Raised when a referenced resource does not exist."""

    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} not found: {resource_id}")


def get_record(model, ident):
    instance = db.session.get(model, ident)
    if instance is None:
        raise ResourceNotFound(model.__name__, ident)
    return instance


def check_teacher_owns_course(teacher_id, course_id):
    return (
        Course.query.filter_by(id=course_id, teacher_id=teacher_id).first() is not None
    )


def check_student_enrolled(student_id, course_id):
    return (
        Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE,
        ).first()
        is not None
    )


def require_teacher_course(teacher_id, course_id):
    course = Course.query.filter_by(id=course_id, teacher_id=teacher_id).first()
    if course is None:
        log_idor_attempt("course", course_id)
        raise AccessDenied("course", course_id)
    return course


def require_teacher_grade(teacher_id, grade_id):
    grade = get_record(Grade, grade_id)
    require_teacher_course(teacher_id, grade.course_id)
    return grade


def require_student_grade(student_id, grade_id):
    grade = get_record(Grade, grade_id)
    if grade.student_id != student_id:
        log_idor_attempt("grade", grade_id, {"student_id": student_id})
        raise AccessDenied("grade", grade_id, {"student_id": student_id})
    return grade


def require_student_attendance(student_id, attendance_id):
    record = get_record(Attendance, attendance_id)
    if record.student_id != student_id:
        log_idor_attempt("attendance", attendance_id, {"student_id": student_id})
        raise AccessDenied("attendance", attendance_id, {"student_id": student_id})
    return record


def require_student_resource(student_id, resource_student_id):
    if resource_student_id != student_id:
        log_idor_attempt("user", resource_student_id, {"student_id": student_id})
        raise AccessDenied("user", resource_student_id, {"student_id": student_id})


def require_role(user, role):
    if not user or not getattr(user, "is_authenticated", True):
        return False
    return user.role == role
