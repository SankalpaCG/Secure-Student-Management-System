from app.admin import admin_bp

from app.admin.routes import courses, dashboard, directories, records, security, users  # noqa: F401, E402

__all__ = ["admin_bp"]
