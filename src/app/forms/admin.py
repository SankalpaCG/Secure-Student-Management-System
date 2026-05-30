from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from app.models.enums import UserRole
from app.utils.password_validators import StrongPassword
from app.models.student_profile import StudentProfile
from app.models.teacher_profile import TeacherProfile
from app.models.user import User


class UserFilterForm(FlaskForm):
    search = StringField("Search", validators=[Optional()])
    role = SelectField(
        "Role",
        choices=[("", "All roles")] + [(r.value, r.value) for r in UserRole],
        validators=[Optional()],
    )
    status = SelectField(
        "Status",
        choices=[("", "All"), ("active", "Active"), ("inactive", "Inactive")],
        validators=[Optional()],
    )
    submit = SubmitField("Filter")


class CreateUserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=10, max=128), StrongPassword()],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    role = SelectField(
        "Role",
        choices=[(r.value, r.value) for r in UserRole],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Active", default=True)
    student_number = StringField("Student Number", validators=[Optional(), Length(max=50)])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    emergency_contact = StringField("Emergency Contact", validators=[Optional(), Length(max=150)])
    staff_number = StringField("Staff Number", validators=[Optional(), Length(max=50)])
    department = StringField("Department", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Create User")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("Email is already registered.")

    def validate_student_number(self, field):
        if self.role.data == UserRole.STUDENT.value and not field.data:
            raise ValidationError("Student number is required for students.")
        if field.data and StudentProfile.query.filter_by(student_number=field.data.strip()).first():
            raise ValidationError("Student number already exists.")

    def validate_staff_number(self, field):
        if self.role.data == UserRole.TEACHER.value and not field.data:
            raise ValidationError("Staff number is required for teachers.")
        if field.data and TeacherProfile.query.filter_by(staff_number=field.data.strip()).first():
            raise ValidationError("Staff number already exists.")


class EditUserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField(
        "Role",
        choices=[(r.value, r.value) for r in UserRole],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Active")
    password = PasswordField(
        "New Password",
        validators=[Optional(), Length(min=10, max=128), StrongPassword()],
        description="Leave blank to keep current password.",
    )
    student_number = StringField("Student Number", validators=[Optional(), Length(max=50)])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    emergency_contact = StringField("Emergency Contact", validators=[Optional(), Length(max=150)])
    staff_number = StringField("Staff Number", validators=[Optional(), Length(max=50)])
    department = StringField("Department", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Save Changes")

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def validate_email(self, field):
        email = field.data.strip().lower()
        existing = User.query.filter(User.email == email)
        if self._user:
            existing = existing.filter(User.id != self._user.id)
        if existing.first():
            raise ValidationError("Email is already in use.")


class CourseForm(FlaskForm):
    course_code = StringField("Course Code", validators=[DataRequired(), Length(max=20)])
    course_name = StringField("Course Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    teacher_id = SelectField("Assigned Teacher", coerce=int, validators=[DataRequired()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Course")


def _optional_int(value):
    if value in (None, "", "0"):
        return None
    return int(value)


class RecordFilterForm(FlaskForm):
    search = StringField("Search", validators=[Optional()])
    course_id = SelectField("Course", coerce=_optional_int, validators=[Optional()])
    student_id = SelectField("Student", coerce=_optional_int, validators=[Optional()])
    teacher_id = SelectField("Teacher", coerce=_optional_int, validators=[Optional()])
    status = SelectField("Status", choices=[("", "All")], validators=[Optional()])
    date_from = DateField("From", validators=[Optional()])
    date_to = DateField("To", validators=[Optional()])
    severity = SelectField(
        "Severity",
        choices=[
            ("", "All"),
            ("CRITICAL", "Critical"),
            ("HIGH", "High"),
            ("MEDIUM", "Medium"),
            ("LOW", "Low"),
            ("INFO", "Info"),
        ],
        validators=[Optional()],
    )
    action = StringField("Action", validators=[Optional()])
    user_id = SelectField("User", coerce=_optional_int, validators=[Optional()])
    submit = SubmitField("Apply Filters")
