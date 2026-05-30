from datetime import datetime

from app.extensions import db
from app.models.enums import EnrollmentStatus


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),
        db.Index("ix_enrollments_student_course", "student_id", "course_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = db.Column(
        db.Enum(EnrollmentStatus, name="enrollment_status", native_enum=False, length=20),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
        server_default="Active",
        index=True,
    )
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship(
        "User",
        back_populates="enrollments",
        foreign_keys=[student_id],
    )
    course = db.relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment student={self.student_id} course={self.course_id}>"
