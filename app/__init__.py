#!/usr/bin/python3
"""flask application instances"""
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Flask application instance
app = Flask(__name__)
# Flask configuration
app.config.from_object(Config)
# Flask-SQLAlchemy and Flask-Migrate initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Flask-Login initialization
login = LoginManager(app)


from app import routes, models
