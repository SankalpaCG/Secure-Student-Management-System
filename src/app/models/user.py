from flask_login import UserMixin

from app.extensions import db
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum(UserRole, name="user_role", native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="1")
    is_2fa_enabled = db.Column(db.Boolean, nullable=False, default=False, server_default="0")
    totp_secret = db.Column(db.String(64), nullable=True)

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    teacher_profile = db.relationship(
        "TeacherProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    courses_taught = db.relationship(
        "Course",
        back_populates="teacher",
        foreign_keys="Course.teacher_id",
        lazy="dynamic",
    )
    enrollments = db.relationship(
        "Enrollment",
        back_populates="student",
        foreign_keys="Enrollment.student_id",
        lazy="dynamic",
    )
    grades_received = db.relationship(
        "Grade",
        back_populates="student",
        foreign_keys="Grade.student_id",
        lazy="dynamic",
    )
    grades_recorded = db.relationship(
        "Grade",
        back_populates="teacher",
        foreign_keys="Grade.teacher_id",
        lazy="dynamic",
    )
    attendance_records = db.relationship(
        "Attendance",
        back_populates="student",
        foreign_keys="Attendance.student_id",
        lazy="dynamic",
    )
    attendance_marked = db.relationship(
        "Attendance",
        back_populates="teacher",
        foreign_keys="Attendance.teacher_id",
        lazy="dynamic",
    )
    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user",
        lazy="dynamic",
    )
    recovery_codes = db.relationship(
        "RecoveryCode",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def to_public_dict(self):
        """Serialize user for API responses — excludes password_hash and totp_secret."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_2fa_enabled": self.is_2fa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
