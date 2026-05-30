from flask import session
from flask_login import login_user, logout_user

from app.extensions import db
from app.models.user import User
from app.utils.helpers import dashboard_url_for_role, is_safe_url


SESSION_PRE_2FA_USER = "pre_2fa_user_id"
SESSION_REMEMBER_ME = "remember_me"
SESSION_2FA_VERIFIED = "2fa_verified"
SESSION_PENDING_TOTP = "pending_totp_secret"
SESSION_RECOVERY_CODES_DISPLAY = "recovery_codes_display"


def get_pre_2fa_user():
    """Return the user awaiting 2FA, or None."""
    user_id = session.get(SESSION_PRE_2FA_USER)
    if not user_id:
        return None
    return db.session.get(User, user_id)


def start_pre_2fa(user, remember=False):
    """Begin the 2FA flow after successful password verification."""
    session[SESSION_PRE_2FA_USER] = user.id
    session[SESSION_REMEMBER_ME] = remember
    session.pop(SESSION_2FA_VERIFIED, None)
    session.pop(SESSION_PENDING_TOTP, None)


def clear_auth_session():
    """Clear all authentication-related session keys."""
    for key in (
        SESSION_PRE_2FA_USER,
        SESSION_REMEMBER_ME,
        SESSION_2FA_VERIFIED,
        SESSION_PENDING_TOTP,
        SESSION_RECOVERY_CODES_DISPLAY,
    ):
        session.pop(key, None)


def is_2fa_verified():
    return session.get(SESSION_2FA_VERIFIED) is True


def complete_login(user, next_url=None):
    """Mark the user as fully authenticated after 2FA succeeds."""
    remember = session.pop(SESSION_REMEMBER_ME, False)
    session.pop(SESSION_PRE_2FA_USER, None)
    session.pop(SESSION_PENDING_TOTP, None)
    session[SESSION_2FA_VERIFIED] = True
    login_user(user, remember=remember)

    if next_url and is_safe_url(next_url):
        return next_url
    return None


def logout_fully():
    """Log out and clear all auth session state."""
    clear_auth_session()
    logout_user()
