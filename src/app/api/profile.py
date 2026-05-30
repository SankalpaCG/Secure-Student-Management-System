from flask import g

from app.api import api_bp
from app.api.decorators import jwt_required
from app.api.serializers import profile_summary
from app.student import services as student_svc


@api_bp.route("/profile", methods=["GET"])
@jwt_required
def api_profile():
    user = g.api_user
    profile = profile_summary(user)
    from app.models.enums import UserRole

    if user.role == UserRole.STUDENT:
        extra = student_svc.get_profile_display(user)
        if extra:
            profile["profile"] = {
                k: v
                for k, v in extra.items()
                if k not in ("email", "full_name")
            }
    return {"profile": profile}
