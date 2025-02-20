"""Database Models"""
from app import db, login
from datetime import datetime, timezone
from enum import Enum
from flask_login import UserMixin
from hashlib import md5
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so


class User(UserMixin, db.Model):
    """User database model"""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    # bookings = db.relationship('Booking', backref='client', lazy='dynamic')
    cars: so.WriteOnlyMapped['Car'] = so.relationship(back_populates='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def avatar(self, size):
    #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
    #         digest, size)


class CarStatus(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    BOOKED = 'booked'


class Car(db.Model):
    """Car database model"""
    __tablename__ = 'car'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    make: so.Mapped[str] = so.mapped_column(sa.String(140))
    model: so.Mapped[str] = so.mapped_column(sa.String(140))
    year: so.Mapped[str] = so.mapped_column(sa.String(140))
    reg_num: so.Mapped[str] = so.mapped_column(sa.String(140))
    fuel_type: so.Mapped[str] = so.mapped_column(sa.String(140))
    mileage: so.Mapped[str] = so.mapped_column(sa.String(140))
    status: so.Mapped[str] = so.mapped_column(sa.String(140), default=CarStatus.AVAILABLE.value)
    timestamp:so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id:so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    # bookings = db.relationship('Booking', backref='car', lazy='dynamic')
    owner: so.Mapped[User] = so.relationship(back_populates='cars')

    # def is_available(self, start_date, end_date):
    #     """ Check if there are any bookings that overlap with the specified date range """
    #     overlapping_bookings = Booking.query.filter(
    #         Booking.car == self,
    #         Booking.start_date <= end_date,
    #         Booking.end_date >= start_date
    #     ).all()

        # return not overlapping_bookings

    def __repr__(self):
        return '<Car {}>'.format(self.make)


class BookingStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Booking(db.Model):
    """Bookings database model"""
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(140), default=BookingStatus.PENDING.value)
    start_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))

    def __repr__(self):
        return '<Status {}>'.format(self.status)


@login.user_loader
def load_user(id):
    """Flask-Login user loader function"""
    return db.session.get(User, int(id))
