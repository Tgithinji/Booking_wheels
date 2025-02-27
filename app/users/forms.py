from app.models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from app import db
import sqlalchemy as sa


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = db.session.scalar(
                sa.select(User).where(User.email == email.data)
            )
            if user is not None:
                raise ValidationError('Please use a different email address.')
