from datetime import datetime, timezone
import secrets
import os
from flask import current_app
from PIL import Image


def check_and_update_bookings():
    from app.models import Booking, BookingStatus, CarStatus

    now = datetime.now(timezone.utc)
    expired_bookings = Booking.query.filter(
        Booking.end_date < now,
        Booking.status == BookingStatus.ACCEPTED.value
    ).all()

    for booking in expired_bookings:
        booking.car.status = CarStatus.AVAILABLE.value
        booking.status = 'completed'


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    output_size = (800, 400)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn


def calculate_booking_price(car, start_date, end_date):
    days = (end_date - start_date).days
    days = max(days, 1)
    return car.price * days