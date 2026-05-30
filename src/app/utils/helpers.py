from urllib.parse import urlparse, urljoin

from flask import request

from app.models.enums import UserRole


def is_safe_url(target):
    """Validate that a redirect URL is local to the application."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def dashboard_url_for_role(role):
    """Return the dashboard endpoint name for a user role."""
    mapping = {
        UserRole.ADMIN: "admin.dashboard",
        UserRole.TEACHER: "teacher.dashboard",
        UserRole.STUDENT: "student.dashboard",
    }
    return mapping.get(role, "index")
