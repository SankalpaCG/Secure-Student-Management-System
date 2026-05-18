"""Student module business logic."""

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import AttendanceStatus, EnrollmentStatus
from app.models.grade import Grade
from app.admin.services import decrypt_student_profile
def _parse_grade(value):
    try:
        v = float(str(value).strip())
        if 0 <= v <= 100:
            return v
    except (TypeError, ValueError):
        pass
    return None


def active_enrollments(student_id):
    return (
        Enrollment.query.filter_by(student_id=student_id, status=EnrollmentStatus.ACTIVE)
        .options(joinedload(Enrollment.course).joinedload(Course.teacher))
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )


def enrolled_course_ids(student_id):
    return {
        e.course_id
        for e in Enrollment.query.filter_by(
            student_id=student_id, status=EnrollmentStatus.ACTIVE
        ).all()
    }


def overall_attendance_pct(student_id):
    total = Attendance.query.filter_by(student_id=student_id).count()
    if total == 0:
        return None
    present = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
    ).count()
    return round((present / total) * 100, 1)


def gpa_average(student_id):
    grades = Grade.query.filter_by(student_id=student_id).all()
    values = [_parse_grade(g.grade_value) for g in grades]
    values = [v for v in values if v is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def recent_grades(student_id, limit=6):
    return (
        Grade.query.options(joinedload(Grade.course), joinedload(Grade.teacher))
        .filter_by(student_id=student_id)
        .order_by(Grade.updated_at.desc())
        .limit(limit)
        .all()
    )


def attendance_donut(student_id):
    records = Attendance.query.filter_by(student_id=student_id).all()
    counts = {"Present": 0, "Absent": 0, "Late": 0}
    for r in records:
        counts[r.status.value] = counts.get(r.status.value, 0) + 1
    return {"labels": list(counts.keys()), "values": list(counts.values())}


def grade_trend(student_id, limit=12):
    grades = (
        Grade.query.filter_by(student_id=student_id)
        .order_by(Grade.updated_at.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "label": g.assessment_name[:20],
            "value": _parse_grade(g.grade_value),
            "date": g.updated_at.strftime("%m/%d") if g.updated_at else "",
        }
        for g in grades
        if _parse_grade(g.grade_value) is not None
    ]


def get_dashboard_data(user):
    enrollments = active_enrollments(user.id)
    return {
        "student_name": user.full_name,
        "enrollments": enrollments,
        "enrolled_count": len(enrollments),
        "attendance_pct": overall_attendance_pct(user.id),
        "gpa": gpa_average(user.id),
        "recent_grades": recent_grades(user.id),
        "attendance_donut": attendance_donut(user.id),
        "grade_trend": grade_trend(user.id),
        "upcoming_assessments": _upcoming_placeholder(),
    }


def _upcoming_placeholder():
    return [
        {"title": "Midterm Review", "course": "TBD", "date": "Coming soon"},
        {"title": "Final Project", "course": "TBD", "date": "Coming soon"},
    ]


def available_courses(student_id):
    enrolled_ids = enrolled_course_ids(student_id)
    q = Course.query.filter(Course.is_active.is_(True)).options(joinedload(Course.teacher))
    if enrolled_ids:
        q = q.filter(Course.id.notin_(enrolled_ids))
    return q.order_by(Course.course_code).all()


def get_profile_display(user):
    profile = user.student_profile
    if not profile:
        return None
    data = decrypt_student_profile(profile)
    data["full_name"] = user.full_name
    data["email"] = user.email
    return data


def attendance_by_course(student_id):
    """Attendance percentage per enrolled course for charts."""
    enrollments = active_enrollments(student_id)
    rows = []
    for enr in enrollments:
        cid = enr.course_id
        total = Attendance.query.filter_by(student_id=student_id, course_id=cid).count()
        if total == 0:
            pct = 0
        else:
            present = Attendance.query.filter(
                Attendance.student_id == student_id,
                Attendance.course_id == cid,
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
            ).count()
            pct = round((present / total) * 100, 1)
        rows.append({"course": enr.course.course_code, "pct": pct})
    return rows


def all_grades(student_id):
    return (
        Grade.query.options(joinedload(Grade.course), joinedload(Grade.teacher))
        .filter_by(student_id=student_id)
        .order_by(Grade.updated_at.desc())
        .all()
    )


def all_attendance(student_id):
    return (
        Attendance.query.options(joinedload(Attendance.course))
        .filter_by(student_id=student_id)
        .order_by(Attendance.attendance_date.desc())
        .all()
    )
