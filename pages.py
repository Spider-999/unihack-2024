from flask import Blueprint, render_template, redirect, url_for, request, abort, current_app
from flask_login import login_required, current_user
from .forms import UpdateAccountForm, CreatePostForm, PostComment
from .models import Post, Comment
from . import db
import secrets, os
from PIL import Image

pages = Blueprint('pages', __name__)

@pages.route('/')
@pages.route('/acasa')
def index():
    return render_template("pages/home.html", leaderboard_ans = current_user.get_leaderboard_answers(), 
                           leaderboard_streak = current_user.get_leaderboard_streak())

# Save picture
def save_picture(form_picture):
    rand_hex = secrets.token_hex(8)
    _, filext = os.path.splitext(form_picture.filename)
    picture_filename = rand_hex + filext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    output_size = (120, 120)

    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_filename


# Forum
@pages.route('/forum')
@login_required
def forum():
    return render_template("pages/forum.html")

@pages.route('/forum/teme')
@login_required
def forum_teme():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category = 'Teme').order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("pages/forum/teme.html")

@pages.route('/forum/teme/new_post', methods = ['GET','POST'])
@login_required
def new_post():
    post_form = CreatePostForm()
    if post_form.validate_on_submit():
        post = Post(title = post_form.title.data, content = post_form.content.data, 
                    like_count = post_form.likeCount.data, category = "Teme", user=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('pages.forum/teme'))
    
    return render_template("pages/forum/teme/new_post.html")


@pages.route("/forum/post-<int:post_id>", methods=['GET', 'POST'])
@login_required
def forum_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_form = PostComment()
    
    if request.method == 'POST':
        if comment_form.validate_on_submit():
            comment = Comment(content=comment_form.content.data, author=current_user.id, post_id=post_id)
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

# Profil
@pages.route('/account', methods = ['GET','POST'])
def account():
    # Actualizare profil
    update_form = UpdateAccountForm()
    if update_form.validate_on_submit():
        if update_form.picture_data:
            picture_file = save_picture(update_form.picture_data)
            current_user.image_file = picture_file
        
        current_user.useername = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        
        return redirect(url_for('pages.account'))
    elif request.method == 'GET':
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email

    img_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('pages/account.html', image_file=img_file, form=update_form)
        


# Pagini de lectii
@pages.route('/invata')
def invata():
    return render_template("pages/invata.html")

@pages.route('/invata/matematica/')
@login_required
def invata_matematica():
    return render_template("pages/invata/matematica.html")

@pages.route('/invata/informatica/')
@login_required
def invata_informatica():
    return render_template("pages/invata/informatica.html")

@pages.route('/invata/fizica/')
@login_required
def invata_fizica():
    return render_template("pages/invata/fizica.html")


