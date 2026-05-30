from app.extensions import db
from app.models.mixins import TimestampMixin


class Course(TimestampMixin, db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="1")
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    teacher = db.relationship(
        "User",
        back_populates="courses_taught",
        foreign_keys=[teacher_id],
    )
    enrollments = db.relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    grades = db.relationship(
        "Grade",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    attendance_records = db.relationship(
        "Attendance",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Course {self.course_code}>"
