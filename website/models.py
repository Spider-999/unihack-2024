from . import db
from flask_login import UserMixin, current_user
from datetime import datetime, timedelta


# Association tables for the many-to-many relationships
user_badge = db.Table('user_badge',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    user_role = db.Column(db.String(10), nullable=False)
    date_joined = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    streak = db.Column(db.Integer(), default = 0)
    correct_answers = db.Column(db.Integer, default = 0)
    level = db.Column(db.Integer, default = 0)
    experience = db.Column(db.Integer, default = 0)


    # Set time to yesterday for newly created user for last exercise solved
    last_exercise = db.Column(db.DateTime(), nullable=True, default=datetime.now() - timedelta(1))

    # backref -> use the author to get the user who created the post
    # lazy -> load the data in one go from the db
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    questions = db.relationship('Question', backref='user')
    badges = db.relationship('Badge', secondary=user_badge, back_populates='users')


    def update_streak(self):
        today = datetime.now()
        
        # If user has already completed an exercise don't update the streak again
        if self.last_exercise.date() == today.date():
            return
        
        if (today - self.last_exercise).total_seconds() / 3600 < 25:
            self.streak += 1
        else:
            self.streak = 0

        self.last_exercise = today
        db.session.commit()

    def award_badge(self):
        if current_user.correct_answers == 1:
            badge = Badge.query.filter_by(name="Primul Exercitiu").first()
            if badge not in current_user.badges:
                current_user.badges.append(badge)
                db.session.commit()
        if current_user.streak == 1:
            badge = Badge.query.filter_by(name="Prima Zi").first()
            if badge not in current_user.badges:
                current_user.badges.append(badge)
                db.session.commit()

    
    def level_up(self):
        if current_user.level == 0 and current_user.experience >= 10:
            current_user.level = 1
            current_user.experience -= 10
            db.session.commit()
        if current_user.level >= 1 and current_user.level <= 5 and current_user.experience >= 30:
            current_user.level += 1
            current_user.experience -= 30
            db.session.commit()
    

    def get_leaderboard_answers(self):
        return User.query.order_by(User.correct_answers.desc()).all()
    
    def get_leaderboard_days(self):
        return User.query.order_by(User.streak.desc()).all()


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


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False, unique = True)
    lessons = db.relationship('Lesson', backref='grade', lazy=True)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    questions = db.relationship('Question', backref='lesson', lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(256), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    answer = db.Column(db.String(128), nullable = True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    image_file = db.Column(db.String(64), nullable=False, default='profile_pics/default.jpg')
    users = db.relationship('User', secondary=user_badge, back_populates='badges')
    