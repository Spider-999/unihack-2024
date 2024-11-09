from . import db
from flask_login import UserMixin, current_user
from datetime import datetime, timedelta
from random import randint, choice

# Association tables for the many-to-many relationships
user_badge = db.Table('user_badge',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'), primary_key=True)
)

user_quests = db.Table('user_quests', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('quest_id', db.Integer, db.ForeignKey('quest.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    # Reset time details

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
    quests = db.relationship('Quest', secondary='user_quests', backref='quests')
    reset_time = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    
    # Daily data specifically needed for quests
    daily_correct_answers = db.Column(db.Integer, default = 0)
    daily_lessons = db.Column(db.Integer, default = 0)
    daily_experience = db.Column(db.Integer, default = 0)

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

    def quest_refresh(self):
        if len(current_user.quests):
            current_user.quests.clear()
        # random quest selection
        quests = Quest.query.order_by(Quest.questType.desc()).all()
        for x in range(3):
            rand_quest = choice(quests)
            while(True):   # unique quest selection
                unique = True
                for q in current_user.quests:
                    if rand_quest == q:
                        unique = False
                if unique:
                    break
                else:
                    rand_quest = choice(quests)
            current_user.quests.append(rand_quest)
        db.session.commit()


    def daily_refresh(self):
        today = datetime.now()
        if (today - self.reset_time).total_seconds() / 3600 > 24:
            current_user.quest_refresh()
            current_user.daily_correct_answers = 0
            current_user.daily_lessons = 0
            self.reset_time = datetime.now()
            db.session.commit()


    def fetch_quests(self):
        quests = Quest.query.order_by(Quest.questType.desc()).all()
        user_quests = []
        highestQuestType = quests[0].questType
        for i in range(0, 3):
            rand_quest = choice(quests)  
            user_quests.append(rand_quest)
        return user_quests


    def check_quests(self):
        for quest in current_user.quests:
            match quest.questType:
                case 1:   # get certain amount of xp
                    if current_user.daily_experience >= quest.questRequirement and not quest.isCompleted:
                        quest.isCompleted = True
                        current_user.experience += quest.awardedXP
                        db.session.commit()
                    break
                case 2:   # complete certain amount of exercises
                    if current_user.daily_correct_answers >= quest.questRequirement and not quest.isCompleted:
                        quest.isCompleted = True
                        current_user.experience += quest.awardedXP
                        db.session.commit()
                    break
                case 3:
                    if current_user.daily_lessons >= quest.questRequirement and not quest.isCompleted:
                        quest.isCompleted = True
                        current_user.experience += quest.awardedXP
                        db.session.commit()
                    break
                case _:
                    break


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
    

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(128), nullable=False)
    awardedXP = db.Column(db.Integer, nullable=False)   
    questType = db.Column(db.Integer, nullable=False)   # decides the requirement
    questRequirement = db.Column(db.Integer, default=1, nullable=False)   # quantity of whatever the requirement is
    isCompleted = db.Column(db.Boolean, default=False)
    user_id = db.relationship('User', secondary='user_quests', backref='users')

    