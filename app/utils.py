from datetime import datetime, timezone


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
