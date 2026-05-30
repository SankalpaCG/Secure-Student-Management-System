from app.extensions import db
from app.models.mixins import TimestampMixin


class StudentProfile(TimestampMixin, db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    student_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(150), nullable=True)

    user = db.relationship("User", back_populates="student_profile")

    def __repr__(self):
        return f"<StudentProfile {self.student_number}>"
