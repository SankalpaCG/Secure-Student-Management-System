"""Serialize models for JSON API responses."""

from app.models.enums import UserRole


def course_summary(course):
    return {
        "id": course.id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "description": course.description,
        "is_active": course.is_active,
        "teacher_id": course.teacher_id,
        "teacher_name": course.teacher.full_name if course.teacher else None,
    }


def enrollment_json(enrollment):
    course = enrollment.course
    return {
        "id": enrollment.id,
        "course_id": enrollment.course_id,
        "course_code": course.course_code if course else None,
        "course_name": course.course_name if course else None,
        "status": enrollment.status.value,
        "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
    }


def grade_json(grade):
    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "course_id": grade.course_id,
        "course_code": grade.course.course_code if grade.course else None,
        "assessment_name": grade.assessment_name,
        "grade_value": grade.grade_value,
        "feedback": grade.feedback,
        "teacher_id": grade.teacher_id,
        "updated_at": grade.updated_at.isoformat() if grade.updated_at else None,
    }


def attendance_json(record):
    return {
        "id": record.id,
        "student_id": record.student_id,
        "course_id": record.course_id,
        "course_code": record.course.course_code if record.course else None,
        "attendance_date": record.attendance_date.isoformat(),
        "status": record.status.value,
        "remarks": record.remarks,
    }


def audit_log_json(log):
    return {
        "id": log.id,
        "user_id": log.user_id,
        "user_email": log.user.email if log.user else None,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "severity": log.severity,
        "ip_address": log.ip_address,
        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
    }


def user_public(user):
    return user.to_public_dict()


def profile_summary(user):
    data = user.to_public_dict()
    if user.role == UserRole.STUDENT and user.student_profile:
        data["student_number"] = user.student_profile.student_number
    if user.role == UserRole.TEACHER and user.teacher_profile:
        data["staff_number"] = user.teacher_profile.staff_number
        data["department"] = user.teacher_profile.department
    return data
