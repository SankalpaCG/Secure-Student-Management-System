from flask import request, url_for

from app.models.enums import UserRole

# Navigation definitions: endpoint must match Flask route names
ADMIN_NAV = [
    {"label": "Dashboard", "icon": "speedometer2", "endpoint": "admin.dashboard"},
    {"label": "Users", "icon": "people", "endpoint": "admin.users"},
    {"label": "Students", "icon": "mortarboard", "endpoint": "admin.students"},
    {"label": "Teachers", "icon": "person-badge", "endpoint": "admin.teachers"},
    {"label": "Courses", "icon": "journal-bookmark", "endpoint": "admin.courses"},
    {"label": "Enrollments", "icon": "card-checklist", "endpoint": "admin.enrollments"},
    {"label": "Grades", "icon": "award", "endpoint": "admin.grades"},
    {"label": "Attendance", "icon": "calendar-check", "endpoint": "admin.attendance"},
    {"label": "Audit Logs", "icon": "clipboard-data", "endpoint": "admin.audit_logs"},
    {"label": "Security Dashboard", "icon": "shield-lock", "endpoint": "admin.security_dashboard"},
]

TEACHER_NAV = [
    {"label": "Dashboard", "icon": "speedometer2", "endpoint": "teacher.dashboard"},
    {"label": "My Courses", "icon": "journal-bookmark", "endpoint": "teacher.courses"},
    {"label": "Course Students", "icon": "people", "endpoint": "teacher.students_hub"},
    {"label": "Manage Grades", "icon": "award", "endpoint": "teacher.grades_hub"},
    {"label": "Attendance", "icon": "calendar-check", "endpoint": "teacher.attendance_hub"},
    {"label": "Grade Analytics", "icon": "bar-chart-line", "endpoint": "teacher.grade_analytics"},
    {"label": "My Profile", "icon": "person-circle", "endpoint": "teacher.profile"},
]

STUDENT_NAV = [
    {"label": "Dashboard", "icon": "speedometer2", "endpoint": "student.dashboard"},
    {"label": "My Profile", "icon": "person-circle", "endpoint": "student.profile"},
    {"label": "Available Courses", "icon": "journal-plus", "endpoint": "student.courses"},
    {"label": "My Enrollments", "icon": "card-checklist", "endpoint": "student.enrollments"},
    {"label": "My Grades", "icon": "award", "endpoint": "student.grades"},
    {"label": "My Attendance", "icon": "calendar-check", "endpoint": "student.attendance"},
    {"label": "Security Settings", "icon": "shield-lock", "endpoint": "student.security_settings"},
]

# Map related endpoints to parent nav item for active highlighting
ACTIVE_ENDPOINT_GROUPS = {
    "admin.users": [
        "admin.users",
        "admin.create_user",
        "admin.edit_user",
        "admin.view_user",
        "admin.export_users",
    ],
    "admin.students": [
        "admin.students",
        "admin.student_profile",
        "admin.student_grades",
        "admin.student_attendance",
        "admin.student_enrollments",
    ],
    "admin.teachers": ["admin.teachers", "admin.teacher_profile"],
    "admin.courses": [
        "admin.courses",
        "admin.create_course",
        "admin.edit_course",
        "admin.course_students",
    ],
    "admin.audit_logs": ["admin.audit_logs", "admin.export_audit_logs"],
    "teacher.courses": [
        "teacher.courses",
        "teacher.course_students",
        "teacher.student_record",
        "teacher.course_analytics",
        "teacher.course_grades",
        "teacher.course_attendance",
    ],
    "teacher.grades_hub": [
        "teacher.grades_hub",
        "teacher.add_grade",
        "teacher.edit_grade",
        "teacher.course_grades",
    ],
    "teacher.attendance_hub": [
        "teacher.attendance_hub",
        "teacher.mark_attendance",
        "teacher.attendance_history",
        "teacher.course_attendance",
    ],
    "teacher.grade_analytics": ["teacher.grade_analytics", "teacher.course_analytics"],
    "student.profile": ["student.profile", "student.edit_profile"],
    "student.courses": ["student.courses", "student.enroll"],
    "student.grades": ["student.grades", "student.grade_detail"],
    "student.security_settings": [
        "student.security_settings",
        "student.backup_codes",
    ],
}


def get_sidebar_nav(role):
    """Return navigation items for the given user role."""
    mapping = {
        UserRole.ADMIN: ADMIN_NAV,
        UserRole.TEACHER: TEACHER_NAV,
        UserRole.STUDENT: STUDENT_NAV,
    }
    return mapping.get(role, [])


def is_nav_active(nav_endpoint, current_endpoint=None):
    """Determine if a sidebar item should be marked active."""
    current = current_endpoint or request.endpoint
    if not current:
        return False
    if current == nav_endpoint:
        return True
    group = ACTIVE_ENDPOINT_GROUPS.get(nav_endpoint, [])
    return current in group


def nav_item_url(endpoint):
    """Build URL for a nav endpoint, returning # if unavailable."""
    try:
        return url_for(endpoint)
    except Exception:
        return "#"
