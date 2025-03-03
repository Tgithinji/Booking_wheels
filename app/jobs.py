from apscheduler.schedulers.background import BackgroundScheduler
from app import db
from app.models import Car, CarStatus
from datetime import datetime
import sqlalchemy as sa


scheduler = BackgroundScheduler()
scheduler.start()


def update_car_status(car_id):
    """Updates the car status to booked
    """
    car = db.session.scalar(
        sa.select(Car).where(Car.id == car_id)
    )
    if car:
        car.status = CarStatus.BOOKED.value
        db.session.commit()


def schedule_car_booking(car_id, update_date):
    run_time = datetime.combine(update_date, datetime.min.time())
    scheduler.add_job(update_car_status, 'date', run_date=run_time, args=[car_id])
