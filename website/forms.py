from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    username = StringField('Nume Utilizator', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    user_role = SelectField('Rol', choices=['Elev', 'Profesor'], validators=[DataRequired()], default='Elev')
    submit = SubmitField('Inregistrare')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Autentificare')


class UpdateAccountForm(FlaskForm):
    picture = FileField('Schimba Avatarul', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Actualizeaza')


class CreatePostForm(FlaskForm):
    title = StringField('Titlu', validators=[DataRequired()])
    content = TextAreaField('Continut', validators=[DataRequired()])
    submit = SubmitField('Posteaza')


class PostComment(FlaskForm):
    content = TextAreaField('Continut', validators=[DataRequired()])
    submit = SubmitField('Comenteaza')


class QuestionForm(FlaskForm):
    question = StringField('Intrebare')
    submit = SubmitField('Raspunde')