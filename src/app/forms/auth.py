from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=255)],
        render_kw={"placeholder": "you@university.edu", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)],
        render_kw={"placeholder": "Enter your password", "autocomplete": "current-password"},
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")
