from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class TwoFactorSetupForm(FlaskForm):
    token = StringField(
        "Verification Code",
        validators=[
            DataRequired(),
            Length(min=6, max=6),
            Regexp(r"^\d{6}$", message="Enter the 6-digit code from your authenticator app."),
        ],
        render_kw={
            "placeholder": "000000",
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "maxlength": "6",
        },
    )
    submit = SubmitField("Enable Two-Factor Authentication")


class TwoFactorVerifyForm(FlaskForm):
    token = StringField(
        "Authenticator Code",
        validators=[
            Optional(),
            Length(min=6, max=6),
            Regexp(r"^\d{6}$", message="Enter a valid 6-digit code."),
        ],
        render_kw={
            "placeholder": "000000",
            "autocomplete": "one-time-code",
            "inputmode": "numeric",
            "maxlength": "6",
        },
    )
    recovery_code = StringField(
        "Recovery Code",
        validators=[Optional(), Length(min=8, max=12)],
        render_kw={"placeholder": "XXXX-XXXX"},
    )
    submit = SubmitField("Verify")
