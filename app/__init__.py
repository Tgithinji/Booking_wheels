#!/usr/bin/python3
"""flask application instances"""
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
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


from app import routes, models, errors
