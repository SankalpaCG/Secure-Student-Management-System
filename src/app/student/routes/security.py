from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.models.recovery_code import RecoveryCode
from app.student import student_bp
from app.services.audit_service import log_event
from app.utils.decorators import student_required
from app.utils.session_auth import SESSION_RECOVERY_CODES_DISPLAY
from app.utils.totp import generate_recovery_codes, hash_recovery_code


@student_bp.route("/security-settings", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("PROFILE_UPDATE_RATE_LIMIT", "10 per hour"))
@student_required
def security_settings():
    unused_codes = current_user.recovery_codes.filter_by(used_at=None).count()

    if request.method == "POST" and request.form.get("action") == "reset_backup_codes":
        if not current_user.is_2fa_enabled:
            flash("Enable two-factor authentication before generating backup codes.", "warning")
            return redirect(url_for("student.security_settings"))

        RecoveryCode.query.filter_by(user_id=current_user.id).delete()
        plain_codes = generate_recovery_codes()
        for code in plain_codes:
            db.session.add(
                RecoveryCode(user_id=current_user.id, code_hash=hash_recovery_code(code))
            )
        db.session.commit()
        session[SESSION_RECOVERY_CODES_DISPLAY] = plain_codes
        log_event(
            current_user.id,
            "TWO_FA_RESET",
            target_type="user",
            target_id=current_user.id,
            severity="HIGH",
            details={"scope": "backup_codes_regenerated"},
        )
        flash("New backup codes generated. Save them now — they will only be shown once.", "success")
        return redirect(url_for("student.backup_codes"))

    return render_template(
        "student/security_settings.html",
        unused_codes=unused_codes,
        breadcrumb_title="Security Settings",
    )


@student_bp.route("/security/backup-codes")
@student_required
def backup_codes():
    codes = session.pop(SESSION_RECOVERY_CODES_DISPLAY, None)
    if not codes:
        flash("Backup codes are only shown immediately after generation.", "info")
        return redirect(url_for("student.security_settings"))
    return render_template(
        "student/backup_codes.html",
        recovery_codes=codes,
        breadcrumb_title="Backup Codes",
    )
