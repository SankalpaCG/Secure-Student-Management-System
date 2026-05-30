from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.forms.student import EditProfileForm
from app.student import student_bp
from app.student import services as svc
from app.services.audit_service import log_event
from app.utils.decorators import student_required
from app.utils.field_encryption import encrypt_field
from app.utils.sanitize import sanitize_text


@student_bp.route("/profile")
@student_required
def profile():
    profile_data = svc.get_profile_display(current_user)
    if not profile_data:
        flash("Student profile not found.", "danger")
        return redirect(url_for("student.dashboard"))
    return render_template(
        "student/profile.html",
        profile=profile_data,
        breadcrumb_title="My Profile",
    )


@student_bp.route("/profile/edit", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("PROFILE_UPDATE_RATE_LIMIT", "10 per hour"))
@student_required
def edit_profile():
    student_profile = current_user.student_profile
    if not student_profile:
        flash("Student profile not found.", "danger")
        return redirect(url_for("student.dashboard"))

    display = svc.get_profile_display(current_user)
    form = EditProfileForm()
    if display:
        form.phone.data = display.get("phone")
        form.address.data = display.get("address")
        form.emergency_contact.data = display.get("emergency_contact")

    if form.validate_on_submit():
        student_profile.phone = encrypt_field(sanitize_text(form.phone.data or "", 20)) or None
        student_profile.address = encrypt_field(sanitize_text(form.address.data or "", 500)) or None
        student_profile.emergency_contact = encrypt_field(
            sanitize_text(form.emergency_contact.data or "", 150)
        ) or None
        db.session.commit()
        log_event(
            current_user.id,
            "UPDATE_STUDENT_PROFILE",
            target_type="student_profile",
            target_id=student_profile.id,
        )
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    return render_template(
        "student/edit_profile.html",
        form=form,
        profile=display,
        breadcrumb_title="Edit Profile",
    )
