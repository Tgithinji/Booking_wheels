#!/usr/bin/python3
"""flask application instances"""
from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)


from app import routes
