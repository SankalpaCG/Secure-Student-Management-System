from functools import wraps

from flask import abort, redirect, session, url_for
from flask_login import current_user, login_required

from app.models.enums import UserRole
from app.services.audit_service import log_event, log_forbidden_route
from app.utils.session_auth import SESSION_PRE_2FA_USER, is_2fa_verified


def two_factor_required(view_func):
    """Require a completed 2FA session in addition to Flask-Login authentication."""

    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not is_2fa_verified():
            if session.get(SESSION_PRE_2FA_USER):
                return redirect(url_for("auth.verify_2fa"))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    """Restrict access to users with one of the given roles after full 2FA."""
    roles_set = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        @two_factor_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles_set:
                log_forbidden_route([r.value for r in roles_set])
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def admin_required(view_func):
    """Restrict access to Admin users."""
    return roles_required(UserRole.ADMIN)(view_func)


def teacher_required(view_func):
    """Restrict access to Teacher users."""
    return roles_required(UserRole.TEACHER)(view_func)


def student_required(view_func):
    """Restrict access to Student users."""
    return roles_required(UserRole.STUDENT)(view_func)
