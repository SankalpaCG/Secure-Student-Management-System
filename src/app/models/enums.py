import enum


class UserRole(enum.Enum):
    ADMIN = "Admin"
    TEACHER = "Teacher"
    STUDENT = "Student"


class EnrollmentStatus(enum.Enum):
    ACTIVE = "Active"
    DROPPED = "Dropped"
    COMPLETED = "Completed"


class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
