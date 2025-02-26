#!/usr/bin/python3
"""flask application instances"""
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_babel import Babel


def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


# Flask application instance
app = Flask(__name__)
# Flask configuration
app.config.from_object(Config)
# Flask-SQLAlchemy and Flask-Migrate initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Flask-Login initialization
login = LoginManager(app)
login.login_view = 'user_login'

babel = Babel(app, locale_selector=get_locale)


@app.before_request
def before_request():
    from app.utils import check_and_update_bookings
    if current_user.is_authenticated:
        check_and_update_bookings()


from app import routes, models, errors
