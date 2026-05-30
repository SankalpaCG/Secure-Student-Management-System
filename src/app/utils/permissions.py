"""Web-oriented permission helpers (abort on denial)."""

from flask import abort

from app.utils import access_control as ac


def teacher_owns_course(teacher_id, course_id):
    return ac.check_teacher_owns_course(teacher_id, course_id)


def student_enrolled_in_course(student_id, course_id):
    return ac.check_student_enrolled(student_id, course_id)


def get_teacher_course(teacher_id, course_id):
    try:
        return ac.require_teacher_course(teacher_id, course_id)
    except ac.AccessDenied:
        abort(403)


def get_teacher_grade(teacher_id, grade_id):
    try:
        return ac.require_teacher_grade(teacher_id, grade_id)
    except ac.ResourceNotFound:
        abort(404)
    except ac.AccessDenied:
        abort(403)


def get_student_grade(student_id, grade_id):
    try:
        return ac.require_student_grade(student_id, grade_id)
    except ac.ResourceNotFound:
        abort(404)
    except ac.AccessDenied:
        abort(403)


def get_student_attendance(student_id, attendance_id):
    try:
        return ac.require_student_attendance(student_id, attendance_id)
    except ac.ResourceNotFound:
        abort(404)
    except ac.AccessDenied:
        abort(403)


def ensure_student_resource(student_id, resource_student_id):
    try:
        ac.require_student_resource(student_id, resource_student_id)
    except ac.AccessDenied:
        abort(403)


def is_role(user, role):
    return ac.require_role(user, role)


def db_get_or_404(model, ident):
    try:
        return ac.get_record(model, ident)
    except ac.ResourceNotFound:
        abort(404)
