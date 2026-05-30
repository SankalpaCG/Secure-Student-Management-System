from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.forms.teacher import AddGradeForm, EditGradeForm
from app.models.grade import Grade
from app.teacher import teacher_bp
from app.teacher import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import teacher_required
from app.utils.permissions import get_teacher_course, get_teacher_grade, student_enrolled_in_course
from app.utils.sanitize import sanitize_text


def _course_choices(teacher_id):
    courses = svc.assigned_courses(teacher_id)
    return [(c.id, f"{c.course_code} — {c.course_name}") for c in courses]


def _student_choices(course_id):
    enrollments = svc.enrolled_students(course_id)
    return [(e.student_id, e.student.full_name) for e in enrollments]


@teacher_bp.route("/grades")
@teacher_required
def grades_hub():
    courses = svc.assigned_courses(current_user.id)
    return render_template(
        "teacher/grades_hub.html",
        courses=courses,
        breadcrumb_title="Manage Grades",
    )


@teacher_bp.route("/grades/add", methods=["GET", "POST"])
@limiter.limit("30 per hour")
@teacher_required
def add_grade():
    form = AddGradeForm()
    form.course_id.choices = _course_choices(current_user.id)
    if not form.course_id.choices:
        flash("No assigned courses available.", "warning")
        return redirect(url_for("teacher.courses"))

    course_id = (
        request.args.get("course_id", type=int)
        or request.form.get("course_id", type=int)
        or form.course_id.data
    )
    student_id = request.args.get("student_id", type=int) or request.form.get(
        "student_id", type=int
    )
    if course_id:
        get_teacher_course(current_user.id, course_id)
        form.course_id.data = course_id
        form.student_id.choices = _student_choices(course_id)
        if student_id:
            form.student_id.data = student_id
    else:
        form.student_id.choices = []

    if request.method == "POST" and course_id:
        form.course_id.data = course_id
        form.student_id.choices = _student_choices(course_id)

    if form.validate_on_submit():
        course = get_teacher_course(current_user.id, form.course_id.data)
        if not student_enrolled_in_course(form.student_id.data, course.id):
            flash("Student is not enrolled in this course.", "danger")
            return redirect(url_for("teacher.add_grade", course_id=course.id))

        grade = Grade(
            student_id=form.student_id.data,
            course_id=course.id,
            teacher_id=current_user.id,
            assessment_name=sanitize_text(form.assessment_name.data, 100),
            grade_value=str(form.grade_value.data),
            feedback=sanitize_text(form.feedback.data or "", 2000) or None,
        )
        db.session.add(grade)
        db.session.commit()
        log_event(current_user.id, "CREATE_GRADE", target_type="grade", target_id=grade.id)
        flash("Grade recorded successfully.", "success")
        return redirect(url_for("teacher.course_students", course_id=course.id))

    return render_template(
        "teacher/add_grade.html",
        form=form,
        breadcrumb_title="Add Grade",
    )


@teacher_bp.route("/grades/<int:grade_id>/edit", methods=["GET", "POST"])
@limiter.limit("30 per hour")
@teacher_required
def edit_grade(grade_id):
    grade = get_teacher_grade(current_user.id, grade_id)
    course = get_teacher_course(current_user.id, grade.course_id)
    form = EditGradeForm(obj=grade)
    try:
        form.grade_value.data = float(grade.grade_value)
    except (TypeError, ValueError):
        pass

    if form.validate_on_submit():
        grade.grade_value = str(form.grade_value.data)
        grade.feedback = sanitize_text(form.feedback.data or "", 2000) or None
        grade.teacher_id = current_user.id
        db.session.commit()
        log_event(current_user.id, "UPDATE_GRADE", target_type="grade", target_id=grade.id)
        flash("Grade updated successfully.", "success")
        return redirect(url_for("teacher.course_students", course_id=course.id))

    return render_template(
        "teacher/edit_grade.html",
        form=form,
        grade=grade,
        course=course,
        breadcrumb_title="Edit Grade",
    )


@teacher_bp.route("/courses/<int:course_id>/grades")
@teacher_required
def course_grades(course_id):
    """Legacy redirect to add grade for a course."""
    get_teacher_course(current_user.id, course_id)
    return redirect(url_for("teacher.add_grade", course_id=course_id))
