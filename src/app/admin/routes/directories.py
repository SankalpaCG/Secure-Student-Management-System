from flask import flash, redirect, render_template, request, url_for

from app.admin import admin_bp
from app.admin import services as svc
from app.extensions import db
from app.models.course import Course
from app.models.enums import UserRole
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.pagination import Pagination


@admin_bp.route("/students")
@admin_required
def students():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    course_id = request.args.get("course_id", type=int)
    q = svc.students_directory_query(
        search=search or None,
        status=status or None,
        course_id=course_id,
    )
    pagination = Pagination(q, page, 15, "admin.students")
    student_rows = []
    for profile in pagination.items:
        cc, pct = svc.student_stats(profile)
        student_rows.append({"profile": profile, "course_count": cc, "attendance_pct": pct})
    courses = Course.query.filter_by(is_active=True).order_by(Course.course_code).all()
    return render_template(
        "admin/students.html",
        students=student_rows,
        pagination=pagination,
        courses=courses,
        search=search,
        status=status,
        course_id=course_id,
        breadcrumb_title="Student Directory",
    )


@admin_bp.route("/students/<int:user_id>")
@admin_required
def student_profile(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.STUDENT:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))
    data = svc.get_student_detail(user)
    return render_template("admin/student_detail.html", **data, breadcrumb_title=user.full_name)


@admin_bp.route("/students/<int:user_id>/grades")
@admin_required
def student_grades(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.STUDENT:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))
    grades = svc.grades_for_student(user_id)
    return render_template(
        "admin/student_grades.html",
        user=user,
        grades=grades,
        breadcrumb_title=f"{user.full_name} — Grades",
    )


@admin_bp.route("/students/<int:user_id>/attendance")
@admin_required
def student_attendance(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.STUDENT:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))
    records = svc.attendance_for_student(user_id)
    return render_template(
        "admin/student_attendance.html",
        user=user,
        records=records,
        breadcrumb_title=f"{user.full_name} — Attendance",
    )


@admin_bp.route("/students/<int:user_id>/enrollments")
@admin_required
def student_enrollments(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.STUDENT:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))
    enrollments = svc.enrollments_for_student(user_id)
    return render_template(
        "admin/student_enrollments.html",
        user=user,
        enrollments=enrollments,
        breadcrumb_title=f"{user.full_name} — Enrollments",
    )


@admin_bp.route("/teachers")
@admin_required
def teachers():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    department = request.args.get("department", "")
    q = svc.teachers_directory_query(search=search or None, department=department or None)
    pagination = Pagination(q, page, 15, "admin.teachers")
    teacher_rows = []
    for profile in pagination.items:
        teacher_rows.append({
            "profile": profile,
            "course_count": svc.teacher_course_count(profile.user_id),
        })
    return render_template(
        "admin/teachers.html",
        teachers=teacher_rows,
        pagination=pagination,
        search=search,
        department=department,
        breadcrumb_title="Teacher Directory",
    )


@admin_bp.route("/teachers/<int:user_id>")
@admin_required
def teacher_profile(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != UserRole.TEACHER:
        flash("Teacher not found.", "danger")
        return redirect(url_for("admin.teachers"))
    data = svc.get_teacher_detail(user)
    return render_template("admin/teacher_detail.html", **data, breadcrumb_title=user.full_name)
