"""
WTForms for the Rock Art application.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from models import User


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Registration form for new users."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please use a different username.')

    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')


class RockArtForm(FlaskForm):
    """Form for creating/editing rock art records."""
    site = StringField('Site', validators=[DataRequired(), Length(max=100)])
    motif = StringField('Motif', validators=[DataRequired(), Length(max=100)])
    panel = StringField('Panel', validators=[Optional(), Length(max=100)])
    groups = StringField('Groups', validators=[Optional(), Length(max=100)])
    type = SelectField('Type', validators=[Optional()], choices=[])
    date = DateField('Date', validators=[Optional()], format='%Y-%m-%d')
    description = TextAreaField('Description', validators=[Optional()])
    latitude = StringField('Latitude', validators=[Optional()])
    longitude = StringField('Longitude', validators=[Optional()])
    submit = SubmitField('Save')


class ImageUploadForm(FlaskForm):
    """Form for uploading images."""
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload')


class SearchForm(FlaskForm):
    """Form for searching records."""
    query = StringField('Search', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Search')
