from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from .forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        print('hello')
        password_hash = generate_password_hash(form.password.data, method='scrypt')
        user = User(username=form.username.data, email=form.email.data, password=password_hash, user_role=form.user_role.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Inregistrare', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)

            return redirect(url_for('pages.home'))
    
    return render_template('auth/login.html', title='Autentificare', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.index'))