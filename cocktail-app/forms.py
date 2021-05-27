from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    """Form for registering/loggin in a user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

class ListForm(FlaskForm):
    """Form for adding/editing a drink list"""

    name = StringField('List Name', validators=[DataRequired()])
    description = TextAreaField('(Optional) Description')