from app.extensions import db
from app.models.mixins import TimestampMixin


class TeacherProfile(TimestampMixin, db.Model):
    __tablename__ = "teacher_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    staff_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    user = db.relationship("User", back_populates="teacher_profile")

    def __repr__(self):
        return f"<TeacherProfile {self.staff_number}>"
