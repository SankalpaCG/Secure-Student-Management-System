from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.admin import services as svc
from app.extensions import db
from app.forms.admin import CourseForm
from app.models.course import Course
from app.models.enums import UserRole
from app.models.user import User
from app.services.audit_service import log_event
from app.utils.decorators import admin_required
from app.utils.pagination import Pagination
from app.utils.sanitize import sanitize_text


def _teacher_choices():
    teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).order_by(User.full_name).all()
    return [(t.id, t.full_name) for t in teachers]


@admin_bp.route("/courses")
@admin_required
def courses():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    q = svc.courses_query(search=search or None)
    pagination = Pagination(q, page, 15, "admin.courses")
    course_rows = []
    for course in pagination.items:
        course_rows.append({
            "course": course,
            "enrolled": svc.course_enrollment_count(course.id),
        })
    return render_template(
        "admin/courses.html",
        courses=course_rows,
        pagination=pagination,
        search=search,
        breadcrumb_title="Courses",
    )


@admin_bp.route("/courses/create", methods=["GET", "POST"])
@admin_required
def create_course():
    form = CourseForm()
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        existing = Course.query.filter_by(course_code=form.course_code.data.strip().upper()).first()
        if existing:
            flash("Course code already exists.", "danger")
            return render_template("admin/course_form.html", form=form, title="Create Course")
        course = Course(
            course_code=form.course_code.data.strip().upper(),
            course_name=sanitize_text(form.course_name.data, 200),
            description=sanitize_text(form.description.data or "", 2000),
            teacher_id=form.teacher_id.data,
            is_active=form.is_active.data,
        )
        db.session.add(course)
        db.session.commit()
        log_event(
            current_user.id,
            "CREATE_COURSE",
            target_type="course",
            target_id=course.id,
        )
        log_event(
            current_user.id,
            "ASSIGN_TEACHER",
            target_type="course",
            target_id=course.id,
            details={"teacher_id": course.teacher_id},
        )
        flash("Course created successfully.", "success")
        return redirect(url_for("admin.courses"))
    return render_template("admin/course_form.html", form=form, title="Create Course")


@admin_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses"))
    form = CourseForm(obj=course)
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        course.course_name = sanitize_text(form.course_name.data, 200)
        course.description = sanitize_text(form.description.data or "", 2000)
        course.teacher_id = form.teacher_id.data
        course.is_active = form.is_active.data
        db.session.commit()
        log_event(current_user.id, "UPDATE_COURSE", target_type="course", target_id=course.id)
        log_event(
            current_user.id,
            "ASSIGN_TEACHER",
            target_type="course",
            target_id=course.id,
            details={"teacher_id": course.teacher_id},
        )
        flash("Course updated successfully.", "success")
        return redirect(url_for("admin.courses"))
    return render_template("admin/course_form.html", form=form, title="Edit Course", course=course)


@admin_bp.route("/courses/<int:course_id>/students")
@admin_required
def course_students(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses"))
    enrollments = svc.enrollments_for_course(course_id)
    return render_template(
        "admin/course_students.html",
        course=course,
        enrollments=enrollments,
        breadcrumb_title=f"{course.course_code} — Students",
    )
