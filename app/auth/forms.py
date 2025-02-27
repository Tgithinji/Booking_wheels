from app.models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app import db
import sqlalchemy as sa


class SignupForm(FlaskForm):
    """Registration form"""
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')



class UserSignupForm(SignupForm):
    """custom validators for user signup form"""
    def validate_username(self, username):
        user = db.session.scalar(
            sa.select(User).where(User.username == username.data)
        )
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data)
        )
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

