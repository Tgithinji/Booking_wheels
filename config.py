"""configuration module"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """class to store configuration variables"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #Flask-SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTS_PER_PAGE = 10

    LANGUAGES = ['en', 'es']
