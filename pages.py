from flask import Blueprint, render_template
from flask_login import login_user, logout_user

pages = Blueprint('pages', __name__)

@pages.route('/')
@pages.route('/acasa')
def acasa():
    return render_template("")

# Pagini de lectii
@pages.route('/invata')
def invata():
    return render_template("")

@pages.route('/invata/matematica/')
@login_required
def invata_matematica():
    return render_template("")

@pages.route('/invata/informatica/')
@login_required
def invata_informatica():
    return render_template("")

@pages.route('/invata/fizica/')
@login_required
def invata_fizica():
    return render_template("")

@pages.route('/forum')
def forum():
    return render_template("")

@pages.route('/login', methods = ['GET','POST'])
def login():
    #if method.type == 'POST':