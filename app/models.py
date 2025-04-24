"""Database Models"""
from app import db, login
from itsdangerous import URLSafeSerializer as Serializer
from datetime import datetime, timezone, timedelta
from enum import Enum
from flask_login import UserMixin
from hashlib import md5
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app


class User(UserMixin, db.Model):
    """User database model"""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    cars: so.WriteOnlyMapped['Car'] = so.relationship(back_populates='owner', lazy='dynamic')
    bookings: so.WriteOnlyMapped['Booking'] = so.relationship(back_populates='renter', lazy='dynamic')
    role: so.Mapped[str] = so.mapped_column(sa.String(100), default='user')

    def get_reset_token(self, expire_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return db.session.get(User, user_id)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def is_admin(self):
        return self.role == 'admin'


class CarStatus(Enum):
    PENDING = 'Pending'
    AVAILABLE = 'Available'
    BOOKED = 'Booked'


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
    seats: so.Mapped[str] = so.mapped_column(sa.String(50))
    status: so.Mapped[str] = so.mapped_column(sa.String(140), default=CarStatus.AVAILABLE.value)
    timestamp:so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id:so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    owner: so.Mapped[User] = so.relationship(back_populates='cars')
    bookings: so.WriteOnlyMapped['Booking'] = so.relationship(back_populates='car', lazy='dynamic', passive_deletes=True)
    price: so.Mapped[int] = so.mapped_column(sa.Integer(), default=50)
    image: so.Mapped[str] = so.mapped_column(sa.String(500), default="default_car.png")
    
    def __repr__(self):
        return '<Car {}>'.format(self.make)


class BookingStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Booking(db.Model):
    """Bookings database model"""
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    car_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Car.id), index=True)
    renter_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    start_date: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    end_date: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc) + timedelta(days=3)
    )
    status: so.Mapped[str] = so.mapped_column(sa.String(140), default=BookingStatus.PENDING.value)
    timestamp:so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now())
   
    renter:so.Mapped[User] = so.relationship(back_populates='bookings')
    car: so.Mapped[Car] = so.relationship(back_populates='bookings')
    total_price: so.Mapped[int] = so.mapped_column(sa.Integer(), default=50)
    
    @staticmethod
    def is_available(car_id, start_date, end_date):
        existing_booking = db.session.execute(
            sa.select(Booking.start_date, Booking.end_date)
            .where(
                Booking.car_id == car_id,
                Booking.status == BookingStatus.ACCEPTED.value,
                sa.or_(
                    sa.and_(start_date >= Booking.start_date, start_date < Booking.end_date),
                    sa.and_(end_date > Booking.start_date, end_date <= Booking.end_date),
                    sa.and_(start_date <= Booking.start_date, end_date > Booking.end_date),
                    sa.and_(end_date == Booking.start_date)
                )
            )
        ).fetchall()

        return not existing_booking

    def __repr__(self):
        return '<Status {}>'.format(self.status)


@login.user_loader
def load_user(id):
    """Flask-Login user loader function"""
    return db.session.get(User, int(id))
