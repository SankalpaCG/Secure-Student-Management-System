from datetime import datetime

import pyotp
from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user

from app.auth import auth_bp
from app.extensions import db, limiter
from app.forms.auth import LoginForm
from app.forms.two_factor import TwoFactorSetupForm, TwoFactorVerifyForm
from app.models.recovery_code import RecoveryCode
from app.models.user import User
from app.services.audit_service import log_event
from app.utils.helpers import dashboard_url_for_role, is_safe_url
from app.utils.security import verify_password
from app.utils.session_auth import (
    SESSION_PENDING_TOTP,
    SESSION_PRE_2FA_USER,
    SESSION_RECOVERY_CODES_DISPLAY,
    complete_login,
    get_pre_2fa_user,
    is_2fa_verified,
    logout_fully,
    start_pre_2fa,
)
from app.utils.totp import (
    build_provisioning_uri,
    encrypt_totp_secret,
    generate_qr_code_base64,
    generate_recovery_codes,
    generate_totp_secret,
    hash_recovery_code,
    verify_recovery_code_hash,
    verify_totp_code,
)


def _require_pre_2fa_user():
    user = get_pre_2fa_user()
    if not user or not user.is_active:
        flash("Your session has expired. Please sign in again.", "warning")
        return None
    return user


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("LOGIN_RATE_LIMIT", "5 per minute"))
def login():
    if current_user.is_authenticated and is_2fa_verified():
        return redirect(url_for(dashboard_url_for_role(current_user.role)))

    if current_user.is_authenticated and not is_2fa_verified():
        logout_fully()

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.is_active and verify_password(user.password_hash, form.password.data):
            start_pre_2fa(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                session["auth_next"] = next_page

            if user.is_2fa_enabled:
                return redirect(url_for("auth.verify_2fa"))

            return redirect(url_for("auth.setup_2fa"))

        log_event(
            user_id=None,
            action="LOGIN_FAILED",
            target_type="auth",
            severity="HIGH",
            details={"email": email},
        )
        flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/setup-2fa", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("TWO_FACTOR_RATE_LIMIT", "5 per minute"))
def setup_2fa():
    user = _require_pre_2fa_user()
    if not user:
        return redirect(url_for("auth.login"))

    if user.is_2fa_enabled:
        return redirect(url_for("auth.verify_2fa"))

    if SESSION_PENDING_TOTP not in session:
        session[SESSION_PENDING_TOTP] = generate_totp_secret()
        pass

    secret = session[SESSION_PENDING_TOTP]
    provisioning_uri = build_provisioning_uri(secret, user.email)
    qr_code = generate_qr_code_base64(provisioning_uri)

    form = TwoFactorSetupForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(secret)
        if not totp.verify(form.token.data.strip(), valid_window=1):
            log_event(
                user_id=user.id,
                action="TWO_FA_FAILED",
                target_type="user",
                target_id=user.id,
                severity="HIGH",
            )
            flash("Invalid verification code. Please try again.", "danger")
            return render_template(
                "auth/setup_2fa.html",
                form=form,
                qr_code=qr_code,
                secret=secret,
                user=user,
            )

        user.totp_secret = encrypt_totp_secret(secret)
        user.is_2fa_enabled = True

        RecoveryCode.query.filter_by(user_id=user.id).delete()
        plain_codes = generate_recovery_codes()
        for code in plain_codes:
            db.session.add(RecoveryCode(user_id=user.id, code_hash=hash_recovery_code(code)))
        db.session.commit()

        session.pop(SESSION_PENDING_TOTP, None)
        session[SESSION_RECOVERY_CODES_DISPLAY] = plain_codes

        log_event(
            user_id=user.id,
            action="TWO_FA_SETUP",
            target_type="user",
            target_id=user.id,
            severity="MEDIUM",
        )

        next_url = session.pop("auth_next", None)
        dashboard = complete_login(user, next_url=next_url)
        log_event(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            target_type="user",
            target_id=user.id,
            severity="INFO",
        )
        flash("Two-factor authentication has been enabled.", "success")
        if dashboard:
            return redirect(dashboard)
        return redirect(url_for("auth.backup_codes"))

    return render_template(
        "auth/setup_2fa.html",
        form=form,
        qr_code=qr_code,
        secret=secret,
        user=user,
    )


@auth_bp.route("/backup-codes")
def backup_codes():
    if not current_user.is_authenticated or not is_2fa_verified():
        return redirect(url_for("auth.login"))

    codes = session.pop(SESSION_RECOVERY_CODES_DISPLAY, None)
    if not codes:
        flash("Recovery codes are only shown once immediately after setup.", "info")
        return redirect(url_for(dashboard_url_for_role(current_user.role)))

    return render_template(
        "auth/backup_codes.html",
        recovery_codes=codes,
        dashboard_url=url_for(dashboard_url_for_role(current_user.role)),
    )


@auth_bp.route("/verify-2fa", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("TWO_FACTOR_RATE_LIMIT", "5 per minute"))
def verify_2fa():
    user = _require_pre_2fa_user()
    if not user:
        return redirect(url_for("auth.login"))

    if not user.is_2fa_enabled:
        return redirect(url_for("auth.setup_2fa"))

    form = TwoFactorVerifyForm()
    if form.validate_on_submit():
        token = (form.token.data or "").strip()
        recovery = (form.recovery_code.data or "").strip()

        if not token and not recovery:
            flash("Enter your authenticator code or a recovery code.", "danger")
            return render_template("auth/verify_2fa.html", form=form, user=user)

        verified = False
        if token:
            verified = verify_totp_code(user.totp_secret, token)
        elif recovery:
            verified = _verify_user_recovery_code(user, recovery)

        if not verified:
            log_event(
                user_id=user.id,
                action="TWO_FA_FAILED",
                target_type="user",
                target_id=user.id,
                severity="HIGH",
            )
            flash("Invalid verification code. Please try again.", "danger")
            return render_template("auth/verify_2fa.html", form=form, user=user)

        log_event(
            user_id=user.id,
            action="TWO_FA_SUCCESS",
            target_type="user",
            target_id=user.id,
            severity="INFO",
            details={"method": "recovery" if recovery else "totp"},
        )

        next_url = session.pop("auth_next", None)
        dashboard = complete_login(user, next_url=next_url)
        log_event(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            target_type="user",
            target_id=user.id,
            severity="INFO",
        )
        flash("Verification successful. Welcome back!", "success")
        if dashboard:
            return redirect(dashboard)
        return redirect(url_for(dashboard_url_for_role(user.role)))

    return render_template("auth/verify_2fa.html", form=form, user=user)


@auth_bp.route("/logout")
def logout():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.id
    elif session.get(SESSION_PRE_2FA_USER):
        user_id = session.get(SESSION_PRE_2FA_USER)

    logout_fully()
    if user_id:
        log_event(
            user_id=user_id,
            action="LOGOUT",
            target_type="user",
            target_id=user_id,
            severity="INFO",
        )
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("auth.login"))


def _verify_user_recovery_code(user, code):
    for recovery in user.recovery_codes.filter(RecoveryCode.used_at.is_(None)).all():
        if verify_recovery_code_hash(recovery.code_hash, code):
            recovery.used_at = datetime.utcnow()
            db.session.commit()
            return True
    return False
