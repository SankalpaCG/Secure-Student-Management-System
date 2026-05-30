from datetime import timedelta

from flask import Flask, render_template, session
from dotenv import load_dotenv

from app.config import Config
from app.extensions import init_extensions
from app.security import register_security_headers


def create_app(config_class=Config):
    """Application factory for the Secure Student Management System."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    init_extensions(app)
    register_security_headers(app)

    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        from app import models  # noqa: F401

    _register_session_policy(app)
    _register_blueprints(app)
    _register_context_processors(app)
    _register_template_filters(app)
    _register_error_handlers(app)
    _register_api_handlers(app)
    _register_cli(app)

    return app


def _register_api_handlers(app):
    from app.api.errors import register_api_error_handlers

    register_api_error_handlers(app)


def _register_session_policy(app):
    """Enforce session timeout and permanent session lifetime."""

    @app.before_request
    def configure_session():
        session.permanent = True
        app.permanent_session_lifetime = app.config.get(
            "PERMANENT_SESSION_LIFETIME", timedelta(hours=2)
        )


def _register_template_filters(app):
    from app.utils.audit_helpers import SEVERITY_BADGE, get_action_severity

    @app.template_filter("action_severity")
    def action_severity(action):
        return get_action_severity(action)

    @app.template_filter("severity_badge")
    def severity_badge(severity):
        if severity:
            return SEVERITY_BADGE.get(str(severity).upper(), SEVERITY_BADGE.get(severity, "secondary"))
        return "secondary"

    @app.template_filter("grade_badge")
    def grade_badge(value):
        try:
            score = float(str(value).replace("%", "").strip())
        except (TypeError, ValueError):
            return "secondary"
        if score >= 90:
            return "success"
        if score >= 70:
            return "primary"
        if score >= 50:
            return "warning"
        return "danger"


def _register_context_processors(app):
    @app.context_processor
    def inject_ui_context():
        from datetime import datetime, timezone

        from flask_login import current_user

        from app.utils.helpers import dashboard_url_for_role
        from app.utils.navigation import get_sidebar_nav, is_nav_active, nav_item_url
        from app.utils.session_auth import is_2fa_verified

        ctx = {
            "current_year": datetime.now(timezone.utc).year,
            "is_2fa_verified": is_2fa_verified(),
            "is_nav_active": is_nav_active,
            "nav_item_url": nav_item_url,
            "sidebar_nav": [],
            "dashboard_endpoint": "index",
            "breadcrumb_title": None,
        }
        if current_user.is_authenticated and is_2fa_verified():
            ctx["sidebar_nav"] = get_sidebar_nav(current_user.role)
            ctx["dashboard_endpoint"] = dashboard_url_for_role(current_user.role)
        return ctx


def _register_blueprints(app):
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.teacher import teacher_bp
    from app.student import student_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)

    from app.extensions import csrf

    csrf.exempt(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html")


def _register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        from flask import request
        from flask_login import current_user

        from app.services.audit_service import log_event

        log_event(
            user_id=current_user.id if current_user.is_authenticated else None,
            action="UNAUTHORIZED_ACCESS",
            target_type="http",
            target_id=403,
            severity="CRITICAL",
            details={"path": request.path, "endpoint": request.endpoint},
        )
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    @app.errorhandler(429)
    def too_many_requests(error):
        from flask import jsonify, request
        from flask_login import current_user

        from app.services.audit_service import log_event

        log_event(
            user_id=current_user.id if current_user.is_authenticated else None,
            action="RATE_LIMIT_TRIGGERED",
            target_type="http",
            severity="HIGH",
            details={"path": request.path, "endpoint": request.endpoint},
        )
        if request.path.startswith("/api/"):
            return jsonify({"error": "Rate limit exceeded.", "code": "rate_limit"}), 429
        return render_template("errors/429.html"), 429


def _register_cli(app):
    from app.cli import register_cli_commands

    register_cli_commands(app)
