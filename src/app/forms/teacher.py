from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


def _optional_int(value):
    if value in (None, "", "0"):
        return None
    return int(value)


class AddGradeForm(FlaskForm):
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    student_id = SelectField("Student", coerce=int, validators=[DataRequired()])
    assessment_name = StringField("Assessment Name", validators=[DataRequired(), Length(max=100)])
    grade_value = FloatField(
        "Grade",
        validators=[DataRequired(), NumberRange(min=0, max=100)],
    )
    feedback = TextAreaField("Feedback", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Grade")


class EditGradeForm(FlaskForm):
    grade_value = FloatField(
        "Grade",
        validators=[DataRequired(), NumberRange(min=0, max=100)],
    )
    feedback = TextAreaField("Feedback", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Update Grade")


class AttendanceSessionForm(FlaskForm):
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    attendance_date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Load Students")


class AttendanceFilterForm(FlaskForm):
    course_id = SelectField("Course", coerce=_optional_int, validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[
            ("", "All"),
            ("Present", "Present"),
            ("Absent", "Absent"),
            ("Late", "Late"),
        ],
        validators=[Optional()],
    )
    date_from = DateField("From", validators=[Optional()])
    date_to = DateField("To", validators=[Optional()])
    submit = SubmitField("Apply Filters")


class TeacherProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    department = StringField("Department", validators=[Optional(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    submit = SubmitField("Save Profile")
