from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User


# Autorizare si actualizare cont
class RegisterForm(FlaskForm):
    username = StringField('Nume utilizator', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Adresa de email', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[DataRequired(), Length(min=4)])
    passwordConfirm = PasswordField('Confirmarea parolei', validators=[DataRequired(), EqualTo(password)])
    user_role = SelectField('Rol utilizator', choices=['Elev', 'Profesor'], validators=[DataRequired()], default='Elev')
    submit = SubmitField('Inregistreaza-te')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Acest nume este deja folosit!')
        
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Aceasta adresa de email este deja folosita!')
        
    def validate_password(self, password, passwordConfirm):
        user = User.query.filter_by(password = password.data)
        if user:
            username = user.username.data
            raise ValidationError("Utilizatorul " + username + " deja foloseste aceasta parola!")
        if passwordConfirm.data != password.data:
            raise ValidationError("Parola si confirmarea nu se potrivesc!")
        
class LoginForm(FlaskForm):
    username = StringField('Nume utiliaztor', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Adresa de email', validators = [DataRequired(), Email()])
    password = PasswordField('Parola', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Logare')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nume utilizator', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Adresa de email', validators=[DataRequired(), Email()])
    picture = FileField('Schimba Avatarul', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Inregistreaza-te')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Acest nume este deja folosit!')
        
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Aceasta adresa de email este deja folosita!')
        
    
class UpdatePasswordForm(FlaskForm):
    password = PasswordField('Parola', validators=[DataRequired(), Length(min=4)])
    passwordConfirm = PasswordField('Confirmarea parolei', validators=[DataRequired(), EqualTo(password)])

    def validate_password(self, password, passwordConfirm):
        user = User.query.filter_by(password = password.data)
        if user:
            username = user.username.data
            raise ValidationError("Utilizatorul " + username + " deja foloseste aceasta parola!")
        if passwordConfirm.data != password.data:
            raise ValidationError("Parola si confirmarea nu se potrivesc!")


# Legate de forum-uri - postari, comentarii
class PostForm(FlaskForm):
    title = username = StringField('Titlu', validators=[DataRequired(), Length(max=100)], default = 'Titlu postare')
    content = TextAreaField('Continut', validators=[DataRequired(), Length(max = 1500)])
    submit = SubmitField('Posteaza')

class CommentForm(FlaskForm):
    content = TextAreaField('Continut', validators=[DataRequired(), Length(max = 500)])
    submit = SubmitField('Posteaza')

class QuestionForm(FlaskForm):
    question = StringField('Intrebare')
    submit = SubmitField('Raspunde')