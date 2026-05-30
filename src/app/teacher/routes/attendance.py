from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.forms.teacher import AttendanceFilterForm, AttendanceSessionForm
from app.models.attendance import Attendance
from app.models.enums import AttendanceStatus
from app.teacher import teacher_bp
from app.teacher import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import teacher_required
from app.utils.pagination import Pagination
from app.utils.permissions import get_teacher_course, student_enrolled_in_course
from app.utils.sanitize import sanitize_text


def _course_choices(teacher_id):
    courses = svc.assigned_courses(teacher_id)
    return [(c.id, f"{c.course_code} — {c.course_name}") for c in courses]


def _parse_date(value):
    if not value:
        return date.today()
    if hasattr(value, "year"):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def _load_grid(course, grid_date):
    enrollments = svc.enrolled_students(course.id)
    existing = {
        a.student_id: a
        for a in Attendance.query.filter_by(
            course_id=course.id, attendance_date=grid_date
        ).all()
    }
    students = []
    for enr in enrollments:
        rec = existing.get(enr.student_id)
        students.append({
            "student": enr.student,
            "student_number": (
                enr.student.student_profile.student_number
                if enr.student.student_profile
                else "—"
            ),
            "status": rec.status.value if rec else AttendanceStatus.PRESENT.value,
            "remarks": rec.remarks if rec else "",
        })
    return students


@teacher_bp.route("/attendance")
@teacher_required
def attendance_hub():
    courses = svc.assigned_courses(current_user.id)
    pending = svc.pending_attendance_count(current_user.id)
    return render_template(
        "teacher/attendance_hub.html",
        courses=courses,
        pending=pending,
        breadcrumb_title="Attendance",
    )


@teacher_bp.route("/attendance/mark", methods=["GET", "POST"])
@limiter.limit("60 per hour")
@teacher_required
def mark_attendance():
    session_form = AttendanceSessionForm()
    session_form.course_id.choices = _course_choices(current_user.id)
    if not session_form.course_id.choices:
        flash("No assigned courses available.", "warning")
        return redirect(url_for("teacher.courses"))

    if request.method == "POST" and not request.form.get("save_grid"):
        if session_form.validate_on_submit():
            return redirect(
                url_for(
                    "teacher.mark_attendance",
                    course_id=session_form.course_id.data,
                    date=session_form.attendance_date.data.isoformat(),
                )
            )

    course_id = request.args.get("course_id", type=int) or request.form.get("course_id", type=int)
    course = None
    grid_date = _parse_date(request.args.get("date") or request.form.get("attendance_date"))
    students = []

    if course_id:
        course = get_teacher_course(current_user.id, course_id)
        session_form.course_id.data = course_id
        session_form.attendance_date.data = grid_date
        students = _load_grid(course, grid_date)

    if request.method == "POST" and course and request.form.get("save_grid"):
        if request.form.get("mark_all_present"):
            entries = [
                {
                    "student_id": s["student"].id,
                    "status": AttendanceStatus.PRESENT.value,
                    "remarks": None,
                }
                for s in students
            ]
        else:
            entries = []
            for s in students:
                sid = s["student"].id
                if not student_enrolled_in_course(sid, course.id):
                    continue
                raw_remarks = request.form.get(f"remarks_{sid}", "").strip()
                entries.append({
                    "student_id": sid,
                    "status": request.form.get(
                        f"status_{sid}", AttendanceStatus.PRESENT.value
                    ),
                    "remarks": sanitize_text(raw_remarks, 500) if raw_remarks else None,
                })

        count = svc.save_attendance_grid(
            current_user.id, course.id, grid_date, entries
        )
        db.session.commit()
        log_event(
            current_user.id,
            "MARK_ATTENDANCE",
            target_type="course",
            target_id=course.id,
            details={"date": grid_date.isoformat(), "count": count},
        )
        flash(f"Attendance saved for {count} student(s).", "success")
        return redirect(
            url_for(
                "teacher.mark_attendance",
                course_id=course.id,
                date=grid_date.isoformat(),
            )
        )

    return render_template(
        "teacher/mark_attendance.html",
        session_form=session_form,
        course=course,
        students=students,
        grid_date=grid_date,
        statuses=[s.value for s in AttendanceStatus],
        breadcrumb_title="Mark Attendance",
    )


@teacher_bp.route("/attendance/history")
@teacher_required
def attendance_history():
    form = AttendanceFilterForm(request.args, meta={"csrf": False})
    form.course_id.choices = [("", "All courses")] + _course_choices(current_user.id)
    page = request.args.get("page", 1, type=int)
    q = svc.attendance_history_query(
        current_user.id,
        course_id=form.course_id.data,
        status=form.status.data or None,
        date_from=form.date_from.data,
        date_to=form.date_to.data,
    )
    pagination = Pagination(q, page, 20, "teacher.attendance_history")
    return render_template(
        "teacher/attendance_history.html",
        records=pagination.items,
        pagination=pagination,
        filter_form=form,
        breadcrumb_title="Attendance History",
    )


@teacher_bp.route("/courses/<int:course_id>/attendance")
@teacher_required
def course_attendance(course_id):
    get_teacher_course(current_user.id, course_id)
    return redirect(url_for("teacher.mark_attendance", course_id=course_id))
