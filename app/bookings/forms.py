from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField
from wtforms.validators import DataRequired


class BookingForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Book Now')