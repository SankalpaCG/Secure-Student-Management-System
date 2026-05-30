from app.extensions import db
from app.models.mixins import TimestampMixin


class Grade(TimestampMixin, db.Model):
    __tablename__ = "grades"
    __table_args__ = (
        db.Index("ix_grades_student_course", "student_id", "course_id"),
        db.Index("ix_grades_course_teacher", "course_id", "teacher_id"),
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
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assessment_name = db.Column(db.String(100), nullable=False)
    grade_value = db.Column(db.String(20), nullable=False)
    feedback = db.Column(db.Text, nullable=True)

    student = db.relationship(
        "User",
        back_populates="grades_received",
        foreign_keys=[student_id],
    )
    course = db.relationship("Course", back_populates="grades")
    teacher = db.relationship(
        "User",
        back_populates="grades_recorded",
        foreign_keys=[teacher_id],
    )

    def __repr__(self):
        return f"<Grade student={self.student_id} course={self.course_id}>"
