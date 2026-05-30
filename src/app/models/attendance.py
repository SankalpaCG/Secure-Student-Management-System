from datetime import datetime

from app.extensions import db
from app.models.enums import AttendanceStatus


class Attendance(db.Model):
    __tablename__ = "attendances"
    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "course_id",
            "attendance_date",
            name="uq_attendance_student_course_date",
        ),
        db.Index("ix_attendances_course_date", "course_id", "attendance_date"),
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
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(
        db.Enum(AttendanceStatus, name="attendance_status", native_enum=False, length=20),
        nullable=False,
        default=AttendanceStatus.PRESENT,
        server_default="Present",
        index=True,
    )
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    student = db.relationship(
        "User",
        back_populates="attendance_records",
        foreign_keys=[student_id],
    )
    course = db.relationship("Course", back_populates="attendance_records")
    teacher = db.relationship(
        "User",
        back_populates="attendance_marked",
        foreign_keys=[teacher_id],
    )

    def __repr__(self):
        return (
            f"<Attendance student={self.student_id} "
            f"course={self.course_id} date={self.attendance_date}>"
        )
