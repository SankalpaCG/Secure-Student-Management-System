"""Admin module business logic and aggregated queries."""

from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import AttendanceStatus, EnrollmentStatus, UserRole
from app.models.grade import Grade
from app.models.recovery_code import RecoveryCode
from app.models.revoked_token import RevokedToken
from app.models.student_profile import StudentProfile
from app.models.teacher_profile import TeacherProfile
from app.models.user import User
from app.utils.audit_helpers import get_action_severity as _severity_for_action
from app.utils.field_encryption import decrypt_field, encrypt_field
from app.utils.sanitize import sanitize_text


def since_24h():
    return datetime.utcnow() - timedelta(hours=24)


def get_dashboard_data():
    """Aggregate statistics for the admin dashboard."""
    from app.admin.security_services import RATE_LIMIT, _calculate_risk_score

    cutoff = since_24h()
    failed_logins_24h = AuditLog.query.filter(
        AuditLog.action.in_(["LOGIN_FAILED", "login_failure"]),
        AuditLog.timestamp >= cutoff,
    ).count()
    failed_2fa_24h = AuditLog.query.filter(
        AuditLog.action.in_(["TWO_FA_FAILED", "2fa_verification_failed"]),
        AuditLog.timestamp >= cutoff,
    ).count()
    unauthorized_24h = AuditLog.query.filter(
        AuditLog.action.in_(["UNAUTHORIZED_ACCESS", "unauthorized_access"]),
        AuditLog.timestamp >= cutoff,
    ).count()
    rate_limit_24h = AuditLog.query.filter(
        AuditLog.action.in_(RATE_LIMIT),
        AuditLog.timestamp >= cutoff,
    ).count()
    risk_score = _calculate_risk_score(
        failed_logins_24h, failed_2fa_24h, unauthorized_24h, rate_limit_24h
    )
    return {
        "total_users": User.query.count(),
        "total_students": User.query.filter_by(role=UserRole.STUDENT).count(),
        "total_teachers": User.query.filter_by(role=UserRole.TEACHER).count(),
        "active_courses": Course.query.filter_by(is_active=True).count(),
        "total_enrollments": Enrollment.query.filter_by(status=EnrollmentStatus.ACTIVE).count(),
        "failed_logins_24h": failed_logins_24h,
        "failed_2fa": AuditLog.query.filter(
            AuditLog.action.in_(["TWO_FA_FAILED", "2fa_verification_failed"])
        ).count(),
        "failed_2fa_24h": failed_2fa_24h,
        "unauthorized_24h": unauthorized_24h,
        "rate_limit_24h": rate_limit_24h,
        "risk_score": risk_score,
        "role_counts": {
            "Admin": User.query.filter_by(role=UserRole.ADMIN).count(),
            "Teacher": User.query.filter_by(role=UserRole.TEACHER).count(),
            "Student": User.query.filter_by(role=UserRole.STUDENT).count(),
        },
        "enrollment_by_course": (
            db.session.query(Course.course_code, func.count(Enrollment.id))
            .join(Enrollment, Enrollment.course_id == Course.id)
            .filter(Enrollment.status == EnrollmentStatus.ACTIVE)
            .group_by(Course.id, Course.course_code)
            .order_by(func.count(Enrollment.id).desc())
            .limit(8)
            .all()
        ),
        "login_failures_trend": _login_failure_trend(),
        "recent_activity": _recent_activity(15),
    }


def _login_failure_trend(days=7):
    results = []
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        count = AuditLog.query.filter(
            AuditLog.action.in_(["LOGIN_FAILED", "login_failure"]),
            AuditLog.timestamp >= start,
            AuditLog.timestamp < end,
        ).count()
        results.append({"label": day.strftime("%m/%d"), "count": count})
    return results


def _recent_activity(limit=15):
    logs = (
        AuditLog.query.options(joinedload(AuditLog.user))
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp": log.timestamp,
            "user": log.user.full_name if log.user else "System",
            "action": log.action,
            "ip": log.ip_address or "—",
            "severity": log.severity or _severity_for_action(log.action),
        }
        for log in logs
    ]


def users_query(search=None, role=None, status=None):
    q = User.query
    if search:
        term = f"%{search}%"
        q = q.filter(or_(User.full_name.ilike(term), User.email.ilike(term)))
    if role:
        q = q.filter(User.role == UserRole(role))
    if status == "active":
        q = q.filter(User.is_active.is_(True))
    elif status == "inactive":
        q = q.filter(User.is_active.is_(False))
    return q.order_by(User.created_at.desc())


def students_directory_query(search=None, status=None, course_id=None):
    q = (
        db.session.query(StudentProfile)
        .join(User)
        .options(joinedload(StudentProfile.user))
    )
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                User.full_name.ilike(term),
                User.email.ilike(term),
                StudentProfile.student_number.ilike(term),
            )
        )
    if status == "active":
        q = q.filter(User.is_active.is_(True))
    elif status == "inactive":
        q = q.filter(User.is_active.is_(False))
    if course_id:
        q = q.filter(
            User.id.in_(
                db.session.query(Enrollment.student_id).filter_by(
                    course_id=course_id, status=EnrollmentStatus.ACTIVE
                )
            )
        )
    return q.order_by(StudentProfile.student_number)


def student_stats(profile):
    """Course count and attendance percentage for a student."""
    uid = profile.user_id
    course_count = Enrollment.query.filter_by(
        student_id=uid, status=EnrollmentStatus.ACTIVE
    ).count()
    total = Attendance.query.filter_by(student_id=uid).count()
    if total == 0:
        pct = None
    else:
        present = Attendance.query.filter(
            Attendance.student_id == uid,
            Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
        ).count()
        pct = round((present / total) * 100, 1)
    return course_count, pct


def teachers_directory_query(search=None, status=None, department=None):
    q = (
        db.session.query(TeacherProfile)
        .join(User)
        .options(joinedload(TeacherProfile.user))
    )
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                User.full_name.ilike(term),
                User.email.ilike(term),
                TeacherProfile.staff_number.ilike(term),
                TeacherProfile.department.ilike(term),
            )
        )
    if status == "active":
        q = q.filter(User.is_active.is_(True))
    elif status == "inactive":
        q = q.filter(User.is_active.is_(False))
    if department:
        q = q.filter(TeacherProfile.department.ilike(f"%{department}%"))
    return q.order_by(TeacherProfile.staff_number)


def teacher_course_count(teacher_user_id):
    return Course.query.filter_by(teacher_id=teacher_user_id, is_active=True).count()


def courses_query(search=None, teacher_id=None, active_only=None):
    q = Course.query.options(joinedload(Course.teacher))
    if search:
        term = f"%{search}%"
        q = q.filter(or_(Course.course_code.ilike(term), Course.course_name.ilike(term)))
    if teacher_id:
        q = q.filter(Course.teacher_id == teacher_id)
    if active_only == "1":
        q = q.filter(Course.is_active.is_(True))
    elif active_only == "0":
        q = q.filter(Course.is_active.is_(False))
    return q.order_by(Course.course_code)


def course_enrollment_count(course_id):
    return Enrollment.query.filter_by(
        course_id=course_id, status=EnrollmentStatus.ACTIVE
    ).count()


def enrollments_query(course_id=None, student_id=None, status=None):
    q = Enrollment.query.options(
        joinedload(Enrollment.student), joinedload(Enrollment.course)
    )
    if course_id:
        q = q.filter(Enrollment.course_id == course_id)
    if student_id:
        q = q.filter(Enrollment.student_id == student_id)
    if status:
        q = q.filter(Enrollment.status == EnrollmentStatus(status))
    return q.order_by(Enrollment.enrolled_at.desc())


def grades_query(course_id=None, teacher_id=None, student_id=None, search=None):
    q = Grade.query.options(
        joinedload(Grade.student), joinedload(Grade.course), joinedload(Grade.teacher)
    )
    if course_id:
        q = q.filter(Grade.course_id == course_id)
    if teacher_id:
        q = q.filter(Grade.teacher_id == teacher_id)
    if student_id:
        q = q.filter(Grade.student_id == student_id)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Grade.assessment_name.ilike(term),
                Grade.student.has(User.full_name.ilike(term)),
            )
        )
    return q.order_by(Grade.updated_at.desc())


def attendance_query(course_id=None, status=None, date_from=None, date_to=None):
    q = Attendance.query.options(
        joinedload(Attendance.student),
        joinedload(Attendance.course),
        joinedload(Attendance.teacher),
    )
    if course_id:
        q = q.filter(Attendance.course_id == course_id)
    if status:
        q = q.filter(Attendance.status == AttendanceStatus(status))
    if date_from:
        q = q.filter(Attendance.attendance_date >= date_from)
    if date_to:
        q = q.filter(Attendance.attendance_date <= date_to)
    return q.order_by(Attendance.attendance_date.desc())


def audit_logs_query(action=None, user_id=None, severity=None, search=None, date_from=None, date_to=None):
    q = AuditLog.query.options(joinedload(AuditLog.user))
    if action:
        q = q.filter(AuditLog.action == action)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if date_from:
        q = q.filter(AuditLog.timestamp >= date_from)
    if date_to:
        q = q.filter(AuditLog.timestamp <= date_to)
    if severity:
        q = q.filter(AuditLog.severity == severity.upper())
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                AuditLog.action.ilike(term),
                AuditLog.target_type.ilike(term),
                AuditLog.ip_address.ilike(term),
                AuditLog.details.ilike(term),
            )
        )
    return q.order_by(AuditLog.timestamp.desc())


def get_security_dashboard_data():
    """Delegate to security dashboard module."""
    from app.admin.security_services import get_security_dashboard_data as _security_data

    return _security_data()


def reset_user_2fa(user):
    user.totp_secret = None
    user.is_2fa_enabled = False
    RecoveryCode.query.filter_by(user_id=user.id).delete()


def sync_profile_for_role(user, role, profile_data):
    """Create or update role-specific profile when role changes."""
    role = UserRole(role) if isinstance(role, str) else role
    if role == UserRole.STUDENT:
        profile = user.student_profile
        if not profile:
            profile = StudentProfile(user_id=user.id, student_number=profile_data["student_number"])
            db.session.add(profile)
        profile.student_number = profile_data.get("student_number") or profile.student_number
        profile.date_of_birth = profile_data.get("date_of_birth")
        profile.phone = encrypt_field(sanitize_text(profile_data.get("phone"), 20))
        profile.address = encrypt_field(sanitize_text(profile_data.get("address"), 500))
        profile.emergency_contact = encrypt_field(
            sanitize_text(profile_data.get("emergency_contact"), 150)
        )
    elif role == UserRole.TEACHER:
        profile = user.teacher_profile
        if not profile:
            profile = TeacherProfile(user_id=user.id, staff_number=profile_data["staff_number"])
            db.session.add(profile)
        profile.staff_number = profile_data.get("staff_number") or profile.staff_number
        profile.department = sanitize_text(profile_data.get("department"), 100)
        profile.phone = sanitize_text(profile_data.get("phone"), 20)


def decrypt_student_profile(profile):
    if not profile:
        return None
    return {
        "student_number": profile.student_number,
        "date_of_birth": profile.date_of_birth,
        "phone": decrypt_field(profile.phone) if profile.phone else None,
        "address": decrypt_field(profile.address) if profile.address else None,
        "emergency_contact": decrypt_field(profile.emergency_contact)
        if profile.emergency_contact
        else None,
    }


def users_to_csv_rows(users):
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role.value,
            "active": u.is_active,
            "2fa_enabled": u.is_2fa_enabled,
            "created_at": u.created_at.isoformat() if u.created_at else "",
        }
        for u in users
    ]


def enrollments_for_course(course_id):
    return enrollments_query(course_id=course_id).all()


def enrollments_for_student(student_id):
    return enrollments_query(student_id=student_id).all()


def grades_for_student(student_id):
    return grades_query(student_id=student_id).all()


def attendance_for_student(student_id):
    return attendance_query().filter(Attendance.student_id == student_id).all()


def get_student_detail(user):
    profile = user.student_profile
    course_count, attendance_pct = student_stats(profile) if profile else (0, None)
    return {
        "user": user,
        "profile": profile,
        "student_data": decrypt_student_profile(profile),
        "course_count": course_count,
        "attendance_pct": attendance_pct,
        "enrollments": enrollments_for_student(user.id) if profile else [],
    }


def get_teacher_detail(user):
    profile = user.teacher_profile
    courses = Course.query.filter_by(teacher_id=user.id).order_by(Course.course_code).all()
    return {
        "user": user,
        "profile": profile,
        "courses": courses,
        "course_count": len(courses),
    }


def audit_to_csv_rows(logs):
    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "user": log.user.email if log.user else "",
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id or "",
            "ip": log.ip_address or "",
            "user_agent": log.user_agent or "",
            "severity": log.severity or _severity_for_action(log.action),
            "details": log.details or "",
        }
        for log in logs
    ]
