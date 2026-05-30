"""WTForms validators for password policy."""

from wtforms.validators import ValidationError

from app.utils.password_policy import password_policy_summary, validate_password_strength


class StrongPassword:
    """Require OWASP-aligned password complexity."""

    def __init__(self, message=None):
        self.message = message or password_policy_summary()

    def __call__(self, form, field):
        if not field.data:
            return
        errors = validate_password_strength(field.data)
        if errors:
            raise ValidationError("; ".join(errors))
