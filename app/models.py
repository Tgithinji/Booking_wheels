"""Database Models"""
from app import db, login
from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User database model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='client', lazy='dynamic')
    cars = db.relationship('Car', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Car(db.Model):
    """Car database model"""
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(140), nullable=False)
    model = db.Column(db.String(140), nullable=False)
    year = db.Column(db.String(140), nullable=False)
    reg_num = db.Column(db.String(140), nullable=False)
    fuel_type = db.Column(db.String(140), nullable=False)
    mileage = db.Column(db.Integer(), nullable=False)
    seats= db.Column(db.Integer(), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', backref='car', lazy='dynamic')

    def is_available(self, start_date, end_date):
        """ Check if there are any bookings that overlap with the specified date range """
        overlapping_bookings = Booking.query.filter(
            Booking.car == self,
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).all()

        return not overlapping_bookings

    def __repr__(self):
        return '<Car {}>'.format(self.make)


class BookingStatus(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    BOOKED = 'booked'


class Booking(db.Model):
    """Bookings database model"""
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(140), default=BookingStatus.AVAILABLE.value)
    start_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))

    def __repr__(self):
        return '<booking at {}>'.format(self.avalable)


@login.user_loader
def load_user(id):
    """Flask-Login user loader function"""
    return User.query.get(int(id))
