"""Marshmallow schemas for API request validation."""

from marshmallow import Schema, ValidationError, fields, validates_schema


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    totp_code = fields.String(load_only=True, allow_none=True)


class RefreshSchema(Schema):
    refresh_token = fields.String(required=True)


class LogoutSchema(Schema):
    refresh_token = fields.String(required=True)
    access_token = fields.String(load_only=True, allow_none=True)


class EnrollSchema(Schema):
    course_id = fields.Integer(required=True)


class CreateGradeSchema(Schema):
    student_id = fields.Integer(required=True)
    course_id = fields.Integer(required=True)
    assessment_name = fields.String(required=True)
    grade_value = fields.Float(required=True)
    feedback = fields.String(allow_none=True)


class UpdateGradeSchema(Schema):
    grade_value = fields.Float(required=True)
    feedback = fields.String(allow_none=True)


class AttendanceEntrySchema(Schema):
    student_id = fields.Integer(required=True)
    status = fields.String(required=True)
    remarks = fields.String(allow_none=True)


class MarkAttendanceSchema(Schema):
    course_id = fields.Integer(required=True)
    attendance_date = fields.Date(required=True)
    entries = fields.List(fields.Nested(AttendanceEntrySchema), required=True)

    @validates_schema
    def validate_entries(self, data, **kwargs):
        if not data.get("entries"):
            raise ValidationError("At least one attendance entry is required.", "entries")
