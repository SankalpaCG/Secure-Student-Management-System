from app.teacher import teacher_bp

from app.teacher.routes import attendance, courses, dashboard, grades, profile  # noqa: F401, E402

__all__ = ["teacher_bp"]
