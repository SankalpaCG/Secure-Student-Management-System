from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.extensions import limiter
from app.admin import services as svc
from app.admin.services import decrypt_student_profile, reset_user_2fa, sync_profile_for_role, users_to_csv_rows
from app.extensions import db
from app.forms.admin import CreateUserForm, EditUserForm, UserFilterForm
from app.models.enums import UserRole
from app.models.user import User
from app.services.audit_service import log_event
from app.utils.decorators import admin_required
from app.utils.export import csv_response
from app.utils.pagination import Pagination
from app.utils.sanitize import sanitize_text
from app.utils.security import hash_password


def _teacher_choices():
    teachers = User.query.filter_by(role=UserRole.TEACHER, is_active=True).order_by(User.full_name).all()
    return [(0, "— Select —")] + [(t.id, t.full_name) for t in teachers]


@admin_bp.route("/users")
@admin_required
def users():
    form = UserFilterForm(request.args, meta={"csrf": False})
    page = request.args.get("page", 1, type=int)
    q = svc.users_query(
        search=form.search.data,
        role=form.role.data or None,
        status=form.status.data or None,
    )
    pagination = Pagination(q, page, 15, "admin.users")
    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
        filter_form=form,
        breadcrumb_title="Users",
    )


@admin_bp.route("/users/export")
@admin_required
def export_users():
    q = svc.users_query(
        search=request.args.get("search"),
        role=request.args.get("role") or None,
        status=request.args.get("status") or None,
    )
    rows = users_to_csv_rows(q.limit(5000).all())
    log_event(current_user.id, "EXPORT_USERS", target_type="admin", severity="MEDIUM")
    return csv_response(rows, "users", ["id", "full_name", "email", "role", "active", "2fa_enabled", "created_at"])


@admin_bp.route("/users/<int:user_id>")
@admin_required
def view_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    student_data = decrypt_student_profile(user.student_profile)
    teacher = user.teacher_profile
    return render_template(
        "admin/user_detail.html",
        user=user,
        student_data=student_data,
        teacher_profile=teacher,
        breadcrumb_title=user.full_name,
    )


@admin_bp.route("/users/create", methods=["GET", "POST"])
@limiter.limit("20 per hour")
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            full_name=sanitize_text(form.full_name.data, 150),
            email=form.email.data.strip().lower(),
            password_hash=hash_password(form.password.data),
            role=UserRole(form.role.data),
            is_active=form.is_active.data,
        )
        db.session.add(user)
        db.session.flush()
        profile_data = {
            "student_number": form.student_number.data,
            "date_of_birth": form.date_of_birth.data,
            "phone": form.phone.data,
            "address": form.address.data,
            "emergency_contact": form.emergency_contact.data,
            "staff_number": form.staff_number.data,
            "department": form.department.data,
        }
        sync_profile_for_role(user, form.role.data, profile_data)
        db.session.commit()
        log_event(current_user.id, "CREATE_USER", target_type="user", target_id=user.id)
        flash("User created successfully.", "success")
        return redirect(url_for("admin.view_user", user_id=user.id))
    return render_template("admin/user_form.html", form=form, title="Create User", is_create=True)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))

    form = EditUserForm(user=user, obj=user)
    form.role.data = user.role.value
    if user.student_profile:
        sp = decrypt_student_profile(user.student_profile)
        form.student_number.data = sp["student_number"]
        form.date_of_birth.data = sp["date_of_birth"]
        form.phone.data = sp["phone"]
        form.address.data = sp["address"]
        form.emergency_contact.data = sp["emergency_contact"]
    if user.teacher_profile:
        form.staff_number.data = user.teacher_profile.staff_number
        form.department.data = user.teacher_profile.department
        form.phone.data = user.teacher_profile.phone

    if form.validate_on_submit():
        if user.id == current_user.id and not form.is_active.data:
            flash("You cannot deactivate your own account.", "danger")
            return render_template("admin/user_form.html", form=form, title="Edit User", user=user)

        old_role = user.role
        user.full_name = sanitize_text(form.full_name.data, 150)
        user.email = form.email.data.strip().lower()
        user.role = UserRole(form.role.data)
        user.is_active = form.is_active.data
        if form.password.data:
            user.password_hash = hash_password(form.password.data)

        profile_data = {
            "student_number": form.student_number.data,
            "date_of_birth": form.date_of_birth.data,
            "phone": form.phone.data,
            "address": form.address.data,
            "emergency_contact": form.emergency_contact.data,
            "staff_number": form.staff_number.data,
            "department": form.department.data,
        }
        if user.role != old_role:
            log_event(current_user.id, "ASSIGN_ROLE", target_type="user", target_id=user.id)
        sync_profile_for_role(user, user.role, profile_data)
        db.session.commit()
        log_event(current_user.id, "UPDATE_USER", target_type="user", target_id=user.id)
        flash("User updated successfully.", "success")
        return redirect(url_for("admin.view_user", user_id=user.id))

    return render_template("admin/user_form.html", form=form, title="Edit User", user=user)


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("admin.users"))
    user.is_active = False
    db.session.commit()
    log_event(current_user.id, "DEACTIVATE_USER", target_type="user", target_id=user.id, severity="HIGH")
    flash(f"{user.full_name} has been deactivated. Records are preserved.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/assign-role", methods=["GET", "POST"])
@admin_required
def assign_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    if request.method == "POST":
        new_role = request.form.get("role")
        if new_role not in {r.value for r in UserRole}:
            flash("Invalid role selected.", "danger")
            return redirect(url_for("admin.assign_role", user_id=user_id))
        if user.id == current_user.id and new_role != UserRole.ADMIN.value:
            flash("You cannot remove your own admin access.", "danger")
            return redirect(url_for("admin.assign_role", user_id=user_id))
        old_role = user.role
        user.role = UserRole(new_role)
        profile_data = {
            "student_number": request.form.get("student_number"),
            "staff_number": request.form.get("staff_number"),
            "department": request.form.get("department"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "emergency_contact": request.form.get("emergency_contact"),
        }
        sync_profile_for_role(user, new_role, profile_data)
        db.session.commit()
        if old_role != user.role:
            log_event(current_user.id, "ASSIGN_ROLE", target_type="user", target_id=user.id)
        flash("Role assigned successfully.", "success")
        return redirect(url_for("admin.view_user", user_id=user.id))
    return render_template(
        "admin/assign_role.html",
        user=user,
        roles=UserRole,
        breadcrumb_title=f"Assign Role — {user.full_name}",
    )


@admin_bp.route("/users/<int:user_id>/reset-2fa", methods=["POST"])
@admin_required
def reset_2fa(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    reset_user_2fa(user)
    db.session.commit()
    log_event(current_user.id, "RESET_USER_2FA", target_type="user", target_id=user.id, severity="HIGH")
    flash(f"2FA has been reset for {user.full_name}. They must set up authentication again.", "success")
    return redirect(url_for("admin.view_user", user_id=user.id))
