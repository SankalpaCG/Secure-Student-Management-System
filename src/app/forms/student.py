from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class EditProfileForm(FlaskForm):
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    emergency_contact = StringField(
        "Emergency Contact",
        validators=[Optional(), Length(max=150)],
    )
    submit = SubmitField("Save Changes")
