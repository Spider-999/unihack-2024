from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    user_role = db.Column(db.String(10), nullable=False)
    date_joined = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')