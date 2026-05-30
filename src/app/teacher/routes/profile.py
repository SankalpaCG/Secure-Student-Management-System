from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user

from app.extensions import db, limiter
from app.forms.teacher import TeacherProfileForm
from app.teacher import teacher_bp
from app.services.audit_service import log_event
from app.utils.decorators import teacher_required
from app.utils.sanitize import sanitize_text


@teacher_bp.route("/profile", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("PROFILE_UPDATE_RATE_LIMIT", "10 per hour"))
@teacher_required
def profile():
    profile = current_user.teacher_profile
    form = TeacherProfileForm(obj=current_user)
    if profile:
        form.department.data = profile.department
        form.phone.data = profile.phone

    if form.validate_on_submit():
        current_user.full_name = sanitize_text(form.full_name.data, 150)
        if profile:
            profile.department = sanitize_text(form.department.data or "", 100) or None
            profile.phone = sanitize_text(form.phone.data or "", 20) or None
        db.session.commit()
        log_event(current_user.id, "UPDATE_TEACHER_PROFILE", target_type="user", target_id=current_user.id)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("teacher.profile"))

    return render_template(
        "teacher/profile.html",
        form=form,
        profile=profile,
        breadcrumb_title="My Profile",
    )
