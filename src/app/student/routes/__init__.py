from app.student import student_bp

from app.student.routes import (  # noqa: F401, E402
    attendance,
    courses,
    dashboard,
    enrollments,
    grades,
    profile,
    security,
)

__all__ = ["student_bp"]
