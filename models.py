from . import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy.sql import func 

class User(db.Model, UserMixin):
    id= db.Column(db.Integer(), primary_key= True)
    username= db.Column(db.String(20), nullable= False, unique= True)
    email = db.Column(db.String(120), nullable= False, unique= True)
    first_name= db.Column(db.String(120), nullable= False)
    last_name= db.Column(db.String(120), nullable= False)
    password= db.Column(db.String(256), nullable= False)
    image_file= db.Column(db.String(20), nullable= False, default= 'default.jpg')
    streak= db.Column(db.Integer(), default= 0)
    #number_of_posts= db.Column(db.Integer(), default= 0)
    #number_of_points= db.Column(db.Integer(), default= 0 )
    correct_answers= db.Column(db.Integer(), default= 0)
    date_joined= db.Column(db.DateTime(), nullable= False, default= func.now())
    user_role= db.Column(db.String(10), nullable= False) 
    
    # Set time to yesterday for newly created user for last exercise solved
    last_exercise= db.Column(db.DateTime(), nullable= True, default= datetime.now() - timedelta(1))
    
    # lazy -> How data is loaded from the database ( load the data in one go from the database )
    # backref -> Use the author to get the user who created the post
    
    posts= db.relationship('Post', backref= 'user', lazy= True)
    comments= db.relationship('Comment', backref= 'user', lazy= 'dynamic')
    questions = db.relationship('Question', backref= 'user')
    
    # defines of User class
    
    # Print object
    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.image_file}, {self.user_role})'
    
    def update_streak(self):
        today= datetime.now()
        
        # If user has already completed an exercise don't update the streak again
        if self.last_exercise.date() == today.date():
            return 
        
        if (today - self.last_exercise).total_seconds() / 3600 < 25:
            self.streak += 1 
        else:
            self.streak = 0
            
        self.last_exercise = today
        db.session.commit()
        
    
    def get_leaderboard_answers(self):
        return User.query.order_by(User.correct_answers.desc()).all()
        
    def get_leaderboard_days(self):
        return User.query.order_by(User.streak.desc()).all()
        
    
class Comment(db.Model):
    id= db.Column(db.Integer(), primary_key= True)
    content= db.Column(db.String(), nullable= False)
    time_posted= db.Column(db.DateTime(timezone= True), default= func.now(), nullable = False)
    post_id= db.Column(db.Integer(), db.ForeignKey('post.id'), nullable= False)
    user_id= db.Column(db.Integer(), db.ForeignKey('user.id'), nullable= False)
    
    
class Post(db.Model):
    id= db.Column(db.Integer(), primary_key= True)
    title= db.Column(db.String(32), nullable = False)
    content= db.Column(db.Text, nullable= False)
    date_posted= db.Column(db.DataTime(timezone= True), default= func.now(), nullable= False)
    comments= db.relationship('Comment', backref= 'post', cascade= 'all, delete-orphan', lazy= 'dynamic')
    user_id= db.Column(db.Integer(), db.ForeignKey('user.id'), nullable= False)
    #number_of_likes= db.Column(db.Integer(), default= 0)
    #number_of_comments= db.Column(db.Integer(), default= 0)
    category= db.Column(db.String(32), nullable= False)

    # defines of Post class

    # Print object
    def __repr__(self):
        return f"User({self.title}, {self.date_posted})"
    
    def get_comments(self):
        return Comment.query.filter_by(post_id= Post.id).order_by(Comment.time_posted)

class Question(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    user_id= db.Column(db.Integer(), db.ForeignKey('user.id'), nullable= False)
    question_text= db.Column(db.String(256), nullable= False)
    lesson_id= db.Column(db.Integer(), db.ForeignKey('lesson.id'), nullable= False)
    number_of_likes= db.Column(db.Integer(), default= 0)
    answer= db.Column(db.String(128), nullable= True)
    completed= db.Column(db.Boolean(),nullable= False, default= False)

class Grade(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    title= db.Column(db.String(), nullable= False, unique= True)
    lessons= db.relationship('Lesson', backref= 'grade', lazy= True)
    
class Lesson(db.Model):
    id= db.Column(db.Integer(), primary_key= True)
    title= db.Column(db.String(128), nullable= False, unique= True)
    grade_id= db.Column(db.Integer(), db.ForeignKey('grade.id'), nullable= False)
    content= db.Column(db.Text, nullable= False)
    questions= db.relationship('Question', backref= 'lesson', lazy= True)
    
    
    
    
    
    
    
    
    
    
    
    