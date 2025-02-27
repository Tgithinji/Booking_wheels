#!/usr/bin/python3
"""flask application instances"""
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
# Flask-Login initialization
login = LoginManager()
login.login_view = 'auth.user_login'

moment = Moment()


def create_app(config_class=Config):
    #Flask application instance
    app = Flask(__name__)
    # Flask configuration
    app.config.from_object(Config)
    # Flask-SQLAlchemy and Flask-Migrate initialization

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.cars import bp as cars_bp
    app.register_blueprint(cars_bp)
    
    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.bookings import bp as bookings_bp
    app.register_blueprint(bookings_bp)

    return app


from app import models
