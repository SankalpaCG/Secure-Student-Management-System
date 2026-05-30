from flask import render_template, request
from flask_login import current_user

from app.admin import admin_bp
from app.admin import services as svc
from app.forms.admin import RecordFilterForm
from app.models.course import Course
from app.models.enums import EnrollmentStatus, UserRole
from app.models.user import User
from app.services.audit_service import log_event
from app.utils.decorators import admin_required
from app.utils.export import csv_response
from app.utils.pagination import Pagination


def _populate_record_filters(form):
    form.course_id.choices = [("", "All courses")] + [
        (c.id, f"{c.course_code} — {c.course_name}") for c in Course.query.order_by(Course.course_code).all()
    ]
    students = User.query.filter_by(role=UserRole.STUDENT).order_by(User.full_name).limit(500).all()
    form.student_id.choices = [("", "All students")] + [(s.id, s.full_name) for s in students]
    teachers = User.query.filter_by(role=UserRole.TEACHER).order_by(User.full_name).all()
    form.teacher_id.choices = [("", "All teachers")] + [(t.id, t.full_name) for t in teachers]


@admin_bp.route("/enrollments")
@admin_required
def enrollments():
    form = RecordFilterForm(request.args, meta={"csrf": False})
    _populate_record_filters(form)
    form.status.choices = [("", "All")] + [(s.value, s.value) for s in EnrollmentStatus]
    page = request.args.get("page", 1, type=int)
    q = svc.enrollments_query(
        course_id=form.course_id.data or None,
        student_id=form.student_id.data or None,
        status=form.status.data or None,
    )
    pagination = Pagination(q, page, 20, "admin.enrollments")
    return render_template(
        "admin/enrollments.html",
        enrollments=pagination.items,
        pagination=pagination,
        filter_form=form,
        breadcrumb_title="Enrollments",
    )


@admin_bp.route("/grades")
@admin_required
def grades():
    form = RecordFilterForm(request.args, meta={"csrf": False})
    _populate_record_filters(form)
    page = request.args.get("page", 1, type=int)
    q = svc.grades_query(
        course_id=form.course_id.data or None,
        student_id=form.student_id.data or None,
        teacher_id=form.teacher_id.data or None,
        search=form.search.data,
    )
    pagination = Pagination(q, page, 20, "admin.grades")
    return render_template(
        "admin/grades.html",
        grades=pagination.items,
        pagination=pagination,
        filter_form=form,
        read_only=True,
        breadcrumb_title="Grades",
    )


@admin_bp.route("/attendance")
@admin_required
def attendance():
    form = RecordFilterForm(request.args, meta={"csrf": False})
    _populate_record_filters(form)
    form.status.choices = [
        ("", "All"),
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]
    page = request.args.get("page", 1, type=int)
    q = svc.attendance_query(
        course_id=form.course_id.data or None,
        status=form.status.data or None,
        date_from=form.date_from.data,
        date_to=form.date_to.data,
    )
    pagination = Pagination(q, page, 20, "admin.attendance")
    return render_template(
        "admin/attendance.html",
        records=pagination.items,
        pagination=pagination,
        filter_form=form,
        breadcrumb_title="Attendance",
    )


@admin_bp.route("/audit-logs")
@admin_required
def audit_logs():
    from app.models.user import User

    form = RecordFilterForm(request.args, meta={"csrf": False})
    form.user_id.choices = [("", "All users")] + [
        (u.id, f"{u.full_name} ({u.email})")
        for u in User.query.order_by(User.full_name).limit(500).all()
    ]
    page = request.args.get("page", 1, type=int)
    q = svc.audit_logs_query(
        action=form.action.data or request.args.get("action"),
        user_id=form.user_id.data or request.args.get("user_id", type=int),
        severity=form.severity.data or None,
        date_from=form.date_from.data,
        date_to=form.date_to.data,
        search=form.search.data or request.args.get("search") or request.args.get("q"),
    )
    pagination = Pagination(q, page, 25, "admin.audit_logs")
    return render_template(
        "admin/audit_logs.html",
        logs=pagination.items,
        pagination=pagination,
        filter_form=form,
        breadcrumb_title="Audit Logs",
    )


@admin_bp.route("/audit-logs/export")
@admin_required
def export_audit_logs():
    q = svc.audit_logs_query(
        action=request.args.get("action"),
        user_id=request.args.get("user_id", type=int),
        severity=request.args.get("severity"),
        search=request.args.get("q") or request.args.get("search"),
    )
    rows = svc.audit_to_csv_rows(q.limit(10000).all())
    log_event(current_user.id, "EXPORT_AUDIT_LOGS", target_type="admin", severity="MEDIUM")
    return csv_response(
        rows,
        "audit_logs",
        [
            "timestamp",
            "user",
            "action",
            "target_type",
            "target_id",
            "ip",
            "browser",
            "severity",
            "details",
        ],
    )
