from datetime import datetime, timezone
import secrets
import os
from flask import current_app
from PIL import Image, ImageOps


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
   
    target_size = (800, 600)

    img = Image.open(form_picture)
    # create a blank canvas with background
    background = Image.new('RGB', target_size, (248,248,248))
    # scale the image to fit within target_size, preserving aspect
    img.thumbnail(target_size, Image.LANCZOS)
    # center it on the background
    x = (target_size[0] - img.width) // 2
    y = (target_size[1] - img.height) // 2
    background.paste(img, (x, y))
    background.save(picture_path, quality=85)
    return picture_fn


def calculate_booking_price(car, start_date, end_date):
    days = (end_date - start_date).days
    days = max(days, 1)
    return car.price * days