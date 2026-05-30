from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from app.api import admin_routes, auth, courses, profile, student_routes, teacher_routes  # noqa: E402, F401
