import secrets
import os
from fileinput import filename
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy import null
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SearchPostForm
from flaskblog.models import PostView, User, Post, PostLike
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        if form.is_blogger.data == True:
            user.is_blogger = True
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))
    searchPostForm = SearchPostForm() 
    
    return render_template('register.html', title='Register', form=form, searchPostForm=searchPostForm)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessfull. Please check username and password', 'danger')
    searchPostForm = SearchPostForm() 
    return render_template('login.html', title='Login', form=form, searchPostForm=searchPostForm)

@app.route("/logout",)
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    
    output_size = (125, 125)
    picture = Image.open(form_picture)
    
    # The thumbnail method modifies the
    # image to contain a thumbnail version of itself, no larger than
    # the given size.
    picture.thumbnail(output_size)
    picture.save(picture_path)

    return picture_filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.new_password.data or form.confirm_password.data:
            if form.new_password.data == form.confirm_password.data:
                if form.password.data:
                    old_password = form.password.data
                    if bcrypt.check_password_hash(current_user.password, old_password):
                        new_hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                        current_user.password = new_hashed_password
                        db.session.commit()
                        logout_user()
                        flash('Password changed successfully!', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('Old password is not correct', 'danger')
                        return redirect(url_for('account'))
                else:
                    flash('Please enter your old password', 'danger')
                    return redirect(url_for('account'))
            else:
                flash('New password and Confirm Password doesnt match!', 'danger')
                return redirect(url_for('account'))
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    user_avatar = url_for('static', filename='profile_pics/' + current_user.image_file)
    searchPostForm = SearchPostForm() 
    return render_template('account.html', title='Account', user_avatar=user_avatar, form=form, searchPostForm=searchPostForm)

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_approved=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    searchPostForm = SearchPostForm()
    return render_template('home.html', posts=posts, searchPostForm=searchPostForm)

@app.route("/search_posts", methods=['GET', 'POST'])
def search_posts():
    searchPostForm = SearchPostForm()
    if searchPostForm.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter(Post.title.like("%" + searchPostForm.search_term.data + "%")).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    return render_template('home.html', posts=posts, searchPostForm=searchPostForm)

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=5)

    searchPostForm = SearchPostForm()
    return render_template('user_posts.html', posts=posts, user=user, searchPostForm=searchPostForm)

def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts_pictures', picture_filename)
    
    picture = Image.open(form_picture)
    picture.save(picture_path)

    return picture_filename

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, description=form.description.data, author=current_user)
        if form.picture.data:
            picture_file = save_post_picture(form.picture.data)
            post.image_file = picture_file
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    searchPostForm = SearchPostForm()
    return render_template('create_post.html', title='New Post', 
        form=form, legend='Create Post', searchPostForm=searchPostForm)

@app.route("/post/<string:slug>")
def post(slug):
    id = int(slug.split('-')[-1])
    post = Post.query.filter_by(id=id).first_or_404()

    # check if user is already in postView table
    post_view = PostView.query.filter_by(post_id=post.id, user_id=current_user.id).count()

    # add a user to the post's view table if not added already
    if post_view == 0:
        post_view = PostView(post_id=post.id, user_id=current_user.id)
        db.session.add(post_view)
        db.session.commit()

    searchPostForm = SearchPostForm()    
    return render_template('post.html', title=post.title, post=post, searchPostForm=searchPostForm)

@app.route("/post/<string:post_title>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_title):
    post = Post.query.filter_by(title=post_title).first_or_404(post_title)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            if post.image_file:
                pictures_path = os.path.join(app.root_path, 'static/posts_pictures', post.image_file)
                os.remove(pictures_path)
            picture_file = save_post_picture(form.picture.data)
            post.image_file = picture_file
        post.title = form.title.data
        post.description = form.description.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', slug=(post.title + '-' + str(post.id))))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.content.data = post.content
        form.submit.label.text = 'Update'

    searchPostForm = SearchPostForm() 
    return render_template('create_post.html', title='Update Post', 
        form=form, legend='Update Post', post_title=post.title, searchPostForm=searchPostForm)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.author != current_user and current_user.is_admin != True:
        abort(403)
    if post.image_file:
        pictures_path = os.path.join(app.root_path, 'static/posts_pictures', post.image_file)
        os.remove(pictures_path)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/posts/approvals")
@login_required
def approvals():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_approved=False).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    searchPostForm = SearchPostForm()
    return render_template('approval_posts.html', posts=posts, searchPostForm=searchPostForm)
    
@app.route("/post/<int:post_id>/approve", methods=['GET', 'POST'])
@login_required
def approve_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404(post_id)
    form = PostForm()
    post.is_approved = True
    db.session.commit()
    flash('Post has been approved!', 'success')
    return redirect(url_for('approvals'))
    
@app.route('/like/<int:post_id>/<reaction>')
@login_required
def react_to_post(post_id, reaction):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if reaction == 'like':
        current_user.like_post(post)
        db.session.commit()
    if reaction == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)

@app.context_processor
def utility_processor():
    # Generate slug from post title and id
    def slug(post):
        return post.title.replace(' ', '-') + '-' + str(post.id)
    return dict(slug=slug)
