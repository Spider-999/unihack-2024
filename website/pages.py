from flask import Blueprint, render_template, current_app, url_for, request, redirect
from flask_login import login_required, current_user
from PIL import Image
import secrets
import os
from .forms import UpdateAccountForm
from . import db


pages = Blueprint('pages', __name__)


def save_picture(form_picture):
    rand_hex = secrets.token_hex(8)
    _, filext = os.path.splitext(form_picture.filename)
    picture_filename = rand_hex + filext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    output_size = (120,120)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    return picture_filename


@pages.route('/')
def home():
    return render_template('base.html', title='Acasa')


@pages.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        db.session.commit()
        
        return redirect(url_for('pages.profile'))

    img_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('pages/profile.html', image_file=img_file, form=form)