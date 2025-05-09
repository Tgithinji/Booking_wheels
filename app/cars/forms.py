from app.models import Car
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from app import db
import sqlalchemy as sa


class NewCar(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    reg_num = StringField('Registration number', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    fuel_type = StringField('Fuel Type', validators=[DataRequired()])
    mileage = StringField('Mileage', validators=[DataRequired()])
    price = IntegerField('Price per day')
    picture = FileField('Car Image(png, jpg)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add')

    def validate_reg_num(self, reg_num):
        car = db.session.scalar(
            sa.select(Car).where(Car.reg_num == reg_num.data)
        )
        if car is not None:
            raise ValidationError('Please use a different registration number.')
