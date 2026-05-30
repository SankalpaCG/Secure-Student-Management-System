from flask import g

from app.api import api_bp
from app.api.decorators import jwt_required
from app.api.serializers import course_summary
from app.admin.services import courses_query
from app.models.enums import UserRole
from app.student import services as student_svc
from app.teacher import services as teacher_svc


@api_bp.route("/courses", methods=["GET"])
@jwt_required
def api_courses():
    user = g.api_user
    if user.role == UserRole.STUDENT:
        available = student_svc.available_courses(user.id)
        enrolled = student_svc.active_enrollments(user.id)
        enrolled_ids = {e.course_id for e in enrolled}
        courses = available + [e.course for e in enrolled if e.course]
        seen = set()
        unique = []
        for c in courses:
            if c.id not in seen:
                seen.add(c.id)
                unique.append(c)
        return {
            "courses": [course_summary(c) for c in unique],
            "enrolled_course_ids": list(enrolled_ids),
        }
    if user.role == UserRole.TEACHER:
        courses = teacher_svc.assigned_courses(user.id)
        return {"courses": [course_summary(c) for c in courses]}
    courses = courses_query().all()
    return {"courses": [course_summary(c) for c in courses]}
