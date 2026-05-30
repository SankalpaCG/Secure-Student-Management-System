"""Teacher module business logic."""

from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import AttendanceStatus, EnrollmentStatus
from app.models.grade import Grade
from app.models.student_profile import StudentProfile
from app.models.user import User


def assigned_courses(teacher_id, active_only=True):
    q = Course.query.filter_by(teacher_id=teacher_id)
    if active_only:
        q = q.filter(Course.is_active.is_(True))
    return q.order_by(Course.course_code).all()


def course_enrollment_count(course_id):
    return Enrollment.query.filter_by(
        course_id=course_id, status=EnrollmentStatus.ACTIVE
    ).count()


def total_enrolled_students(teacher_id):
    course_ids = [c.id for c in assigned_courses(teacher_id)]
    if not course_ids:
        return 0
    return (
        db.session.query(func.count(func.distinct(Enrollment.student_id)))
        .filter(
            Enrollment.course_id.in_(course_ids),
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
        .scalar()
        or 0
    )


def pending_attendance_count(teacher_id, on_date=None):
    """Students enrolled in teacher courses without attendance for the given date."""
    on_date = on_date or date.today()
    count = 0
    for course in assigned_courses(teacher_id):
        student_ids = _active_student_ids(course.id)
        for sid in student_ids:
            exists = Attendance.query.filter_by(
                student_id=sid, course_id=course.id, attendance_date=on_date
            ).first()
            if not exists:
                count += 1
    return count


def recent_grades(teacher_id, limit=8):
    return (
        Grade.query.options(joinedload(Grade.student), joinedload(Grade.course))
        .filter_by(teacher_id=teacher_id)
        .order_by(Grade.updated_at.desc())
        .limit(limit)
        .all()
    )


def grade_distribution(teacher_id):
    """Histogram buckets for numeric grades across teacher's courses."""
    course_ids = [c.id for c in assigned_courses(teacher_id)]
    if not course_ids:
        return {"labels": [], "values": []}
    grades = Grade.query.filter(Grade.course_id.in_(course_ids)).all()
    buckets = {"0-49": 0, "50-59": 0, "60-69": 0, "70-79": 0, "80-89": 0, "90-100": 0}
    for g in grades:
        val = _parse_grade(g.grade_value)
        if val is None:
            continue
        if val < 50:
            buckets["0-49"] += 1
        elif val < 60:
            buckets["50-59"] += 1
        elif val < 70:
            buckets["60-69"] += 1
        elif val < 80:
            buckets["70-79"] += 1
        elif val < 90:
            buckets["80-89"] += 1
        else:
            buckets["90-100"] += 1
    return {"labels": list(buckets.keys()), "values": list(buckets.values())}


def attendance_trend(teacher_id, days=14):
    course_ids = [c.id for c in assigned_courses(teacher_id)]
    if not course_ids:
        return []
    results = []
    for i in range(days - 1, -1, -1):
        day = date.today() - timedelta(days=i)
        total = Attendance.query.filter(
            Attendance.course_id.in_(course_ids),
            Attendance.attendance_date == day,
        ).count()
        if total == 0:
            pct = 0
        else:
            present = Attendance.query.filter(
                Attendance.course_id.in_(course_ids),
                Attendance.attendance_date == day,
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
            ).count()
            pct = round((present / total) * 100, 1)
        results.append({"label": day.strftime("%m/%d"), "pct": pct})
    return results


def get_dashboard_data(teacher_id, teacher_name):
    courses = assigned_courses(teacher_id)
    return {
        "teacher_name": teacher_name,
        "course_count": len(courses),
        "total_students": total_enrolled_students(teacher_id),
        "pending_attendance": pending_attendance_count(teacher_id),
        "recent_grades": recent_grades(teacher_id),
        "grade_distribution": grade_distribution(teacher_id),
        "attendance_trend": attendance_trend(teacher_id),
        "courses": courses,
    }


def course_student_rows(course_id):
    """Enrolled students with attendance % and average grade for a course."""
    enrollments = (
        Enrollment.query.filter_by(course_id=course_id, status=EnrollmentStatus.ACTIVE)
        .options(joinedload(Enrollment.student).joinedload(User.student_profile))
        .all()
    )
    rows = []
    for enr in enrollments:
        student = enr.student
        rows.append({
            "student": student,
            "student_number": (
                student.student_profile.student_number if student.student_profile else "—"
            ),
            "attendance_pct": student_attendance_pct(student.id, course_id),
            "avg_grade": student_avg_grade(student.id, course_id),
        })
    return rows


def student_attendance_pct(student_id, course_id):
    total = Attendance.query.filter_by(student_id=student_id, course_id=course_id).count()
    if total == 0:
        return None
    present = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
    ).count()
    return round((present / total) * 100, 1)


def student_avg_grade(student_id, course_id):
    grades = Grade.query.filter_by(student_id=student_id, course_id=course_id).all()
    values = [_parse_grade(g.grade_value) for g in grades]
    values = [v for v in values if v is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def student_academic_record(student_id, course_id):
    return {
        "grades": Grade.query.filter_by(student_id=student_id, course_id=course_id)
        .order_by(Grade.updated_at.desc())
        .all(),
        "attendance": Attendance.query.filter_by(student_id=student_id, course_id=course_id)
        .order_by(Attendance.attendance_date.desc())
        .all(),
        "attendance_pct": student_attendance_pct(student_id, course_id),
        "avg_grade": student_avg_grade(student_id, course_id),
    }


def course_analytics(course_id):
    grades = Grade.query.filter_by(course_id=course_id).all()
    numeric = [_parse_grade(g.grade_value) for g in grades]
    numeric = [v for v in numeric if v is not None]

    histogram = {"0-49": 0, "50-59": 0, "60-69": 0, "70-79": 0, "80-89": 0, "90-100": 0}
    for val in numeric:
        if val < 50:
            histogram["0-49"] += 1
        elif val < 60:
            histogram["50-59"] += 1
        elif val < 70:
            histogram["60-69"] += 1
        elif val < 80:
            histogram["70-79"] += 1
        elif val < 90:
            histogram["80-89"] += 1
        else:
            histogram["90-100"] += 1

    student_ids = _active_student_ids(course_id)
    performers = []
    at_risk = []
    attendance_rates = []
    for sid in student_ids:
        avg = student_avg_grade(sid, course_id)
        att = student_attendance_pct(sid, course_id)
        student = db.session.get(User, sid)
        if student:
            row = {"name": student.full_name, "avg": avg, "attendance": att}
            performers.append(row)
            attendance_rates.append(att or 0)
            if (avg is not None and avg < 60) or (att is not None and att < 75):
                at_risk.append(row)

    performers.sort(key=lambda x: (x["avg"] is None, -(x["avg"] or 0)))
    at_risk.sort(key=lambda x: (x["avg"] or 0))

    course_att_pct = round(sum(attendance_rates) / len(attendance_rates), 1) if attendance_rates else 0

    return {
        "histogram_labels": list(histogram.keys()),
        "histogram_values": list(histogram.values()),
        "course_attendance_pct": course_att_pct,
        "top_performers": performers[:5],
        "at_risk": at_risk[:5],
        "grade_count": len(grades),
        "student_count": len(student_ids),
    }


def attendance_history_query(teacher_id, course_id=None, status=None, date_from=None, date_to=None):
    course_ids = [c.id for c in assigned_courses(teacher_id, active_only=False)]
    if not course_ids:
        return Attendance.query.filter(False)
    q = Attendance.query.options(
        joinedload(Attendance.student),
        joinedload(Attendance.course),
    ).filter(Attendance.course_id.in_(course_ids))
    if course_id:
        q = q.filter(Attendance.course_id == course_id)
    if status:
        q = q.filter(Attendance.status == AttendanceStatus(status))
    if date_from:
        q = q.filter(Attendance.attendance_date >= date_from)
    if date_to:
        q = q.filter(Attendance.attendance_date <= date_to)
    return q.order_by(Attendance.attendance_date.desc(), Attendance.id.desc())


def save_attendance_grid(teacher_id, course_id, attendance_date, entries):
    """Upsert attendance records. entries: list of dicts with student_id, status, remarks."""
    saved = 0
    for entry in entries:
        student_id = entry["student_id"]
        status = AttendanceStatus(entry["status"])
        remarks = entry.get("remarks")
        existing = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            attendance_date=attendance_date,
        ).first()
        if existing:
            existing.status = status
            existing.remarks = remarks
            existing.teacher_id = teacher_id
        else:
            db.session.add(
                Attendance(
                    student_id=student_id,
                    course_id=course_id,
                    teacher_id=teacher_id,
                    attendance_date=attendance_date,
                    status=status,
                    remarks=remarks,
                    created_at=datetime.utcnow(),
                )
            )
        saved += 1
    return saved


def _active_student_ids(course_id):
    return [
        e.student_id
        for e in Enrollment.query.filter_by(
            course_id=course_id, status=EnrollmentStatus.ACTIVE
        ).all()
    ]


def enrolled_students(course_id):
    return (
        Enrollment.query.filter_by(course_id=course_id, status=EnrollmentStatus.ACTIVE)
        .options(joinedload(Enrollment.student).joinedload(User.student_profile))
        .order_by(Enrollment.student_id)
        .all()
    )


def _parse_grade(value):
    try:
        v = float(str(value).strip())
        if 0 <= v <= 100:
            return v
    except (TypeError, ValueError):
        pass
    return None
