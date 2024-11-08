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

    # backref -> use the author to get the user who created the post
    # lazy -> load the data in one go from the db
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan', lazy='dynamic')


    def get_comments(self):
        return Comment.query.filter_by(post_id=Post.id).order_by(Comment.time_posted)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    time_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)