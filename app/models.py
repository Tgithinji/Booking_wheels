"""Database Models"""
from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User database model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='client', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(UserMixin, db.Model):
    """Admin database model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    cars = db.relationship('Car', backref='owner', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Admin {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Car(db.Model):
    """Car database model"""
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(140), nullable=False)
    model = db.Column(db.String(140), nullable=False)
    year = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    image_file = db.Column(db.String(20), nullable=False, default='')
    bookings = db.relationship('Booking', backref='car', lazy='dynamic')

    def __repr__(self):
        return '<Car {}>'.format(self.make)


class Booking(db.Model):
    """Bookings database model"""
    id = db.Column(db.Integer, primary_key=True)
    avalable = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))

    def __repr__(self):
        return '<booking at {}>'.format(self.avalable)


@login.user_loader
def load_user(id):
    """Flask-Login user loader function"""
    return User.query.get(int(id))
