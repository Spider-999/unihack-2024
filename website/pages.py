from flask import Blueprint, render_template, current_app, url_for, request, redirect, abort, jsonify
from flask_login import login_required, current_user
from PIL import Image
import secrets
import os
from .forms import UpdateAccountForm, CreatePostForm, PostComment
from .models import Post, Comment
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
    return render_template('pages/home.html', title='Acasa')


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
    return render_template('pages/profile.html', image_file=img_file, form=form, experience=current_user.experience, total_experience = 50)


@pages.route('/profile/get_experience')
@login_required
def get_experience():
    print(current_user.experience)
    return jsonify({"experience":current_user.experience})


@pages.route("/forum/teme/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    post_form = CreatePostForm()
    if post_form.validate_on_submit():
        post = Post(title=post_form.title.data, content=post_form.content.data, category='Teme', user=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('pages.forum_teme'))
    
    return render_template('pages/forum/create_post.html', form=post_form, legend='New Post')
    

@pages.route("/forum")
@login_required
def forum():
    return render_template('pages/forum/forum.html')


@pages.route("/forum/teme/")
@login_required
def forum_teme():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category='Teme').order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('pages/forum/forum_teme.html', posts=posts)


@pages.route("/forum/post-<int:post_id>", methods=['GET', 'POST'])
@login_required
def forum_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = PostComment()
    
    if request.method == 'POST':
        if comment_form.validate_on_submit():
            comment = Comment(content=comment_form.content.data, user_id=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()

    comment_form.content.data = ''

    return render_template('pages/forum/post.html', title=post.title, post=post, comment_form=comment_form, comments=post.comments)


@pages.route("/forum/post-<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user != current_user:
        abort(403)

    form = CreatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('pages.forum_post', post_id=post.id))

    form.title.data = post.title
    form.content.data = post.content
    return render_template('pages/forum/create_post.html', form=form, legend='Update Post')


@pages.route("/forum/post-<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('pages.forum_teme'))

@pages.route("/invata")
@login_required
def invata():
    return render_template('pages/invata/invata.html')


@pages.route("/invata/matematica")
@login_required
def invata_matematica():
    return render_template('pages/invata/matematica.html')


@pages.route("/invata/informatica")
@login_required
def invata_info():
    return render_template('pages/invata/informatica.html')