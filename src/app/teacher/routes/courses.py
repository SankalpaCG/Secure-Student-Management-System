from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db
from app.models.user import User
from app.teacher import teacher_bp
from app.teacher import services as svc
from app.utils.decorators import teacher_required
from app.utils.permissions import get_teacher_course, student_enrolled_in_course


@teacher_bp.route("/courses")
@teacher_required
def courses():
    course_rows = []
    for course in svc.assigned_courses(current_user.id):
        course_rows.append({
            "course": course,
            "student_count": svc.course_enrollment_count(course.id),
        })
    return render_template(
        "teacher/courses.html",
        courses=course_rows,
        breadcrumb_title="My Courses",
    )


@teacher_bp.route("/courses/<int:course_id>/students")
@teacher_required
def course_students(course_id):
    course = get_teacher_course(current_user.id, course_id)
    students = svc.course_student_rows(course.id)
    return render_template(
        "teacher/students.html",
        course=course,
        students=students,
        breadcrumb_title=f"{course.course_code} — Students",
    )


@teacher_bp.route("/courses/<int:course_id>/students/<int:student_id>/record")
@teacher_required
def student_record(course_id, student_id):
    course = get_teacher_course(current_user.id, course_id)
    if not student_enrolled_in_course(student_id, course.id):
        flash("Student is not enrolled in this course.", "danger")
        return redirect(url_for("teacher.course_students", course_id=course.id))
    student = db.session.get(User, student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("teacher.course_students", course_id=course.id))
    record = svc.student_academic_record(student_id, course.id)
    return render_template(
        "teacher/student_record.html",
        course=course,
        student=student,
        record=record,
        breadcrumb_title=f"{student.full_name} — Record",
    )


@teacher_bp.route("/courses/<int:course_id>/analytics")
@teacher_required
def course_analytics(course_id):
    course = get_teacher_course(current_user.id, course_id)
    analytics = svc.course_analytics(course.id)
    return render_template(
        "teacher/course_analytics.html",
        course=course,
        breadcrumb_title=f"{course.course_code} — Analytics",
        **analytics,
    )


@teacher_bp.route("/students")
@teacher_required
def students_hub():
    return redirect(url_for("teacher.courses"))


@teacher_bp.route("/grade-analytics")
@teacher_required
def grade_analytics():
    courses = svc.assigned_courses(current_user.id)
    if courses:
        return redirect(url_for("teacher.course_analytics", course_id=courses[0].id))
    return render_template(
        "teacher/grade_analytics.html",
        courses=[],
        breadcrumb_title="Analytics",
    )
