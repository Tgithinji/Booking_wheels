"""Main application module"""
from app import app, db
from app.models import User, Admin, Car, Booking


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Admin': Admin,
            'Car': Car, 'Booking': Booking}
