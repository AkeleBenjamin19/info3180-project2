from datetime import datetime, timezone
import os
from app import app, db, login_manager
from flask import jsonify, render_template, request, redirect, url_for, flash, session, abort,send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile,FollowTable,PostTable,LikeTable
from app.forms import LoginForm,PostForm,RegisterForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename


###
# Routing for postman 
###

@app.route('/api/v1/test', methods=['GET'])
def test():
    alist=["This","is","a","test"]
    return jsonify({'test': 'Testing'}), 200

@app.route('/api/v1/register', methods=['POST'])
def register_user():
    """Render the website's register page."""
    username = request.json.get('username')
    password = request.json.get('password')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    email = request.json.get('email')
    location = request.json.get('location')
    biography = request.json.get('biography')
    filename = request.json.get('profile_photo')
    joined_on=datetime.now(timezone.utc)
    # Check if the username or email already exists in the database
    existing_user = db.session.execute(db.select(UserProfile).filterby((username == username) | (email == email)).first())
    if existing_user:
        return jsonify({'error': 'Username or email already exists.'}), 400
    
    new_user=UserProfile(username,password,firstname,lastname,email,location,biography,filename,joined_on)
    db.session.add(new_user) 
    db.session.commit()
    return jsonify({'message': 'User registered successfully.'}), 201

@app.route('/api/v1/auth/login',methods=['POST'])
def login_user():
    username = request.json.get('username')
    password = request.json.get('password')

    user=db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar_one()
    if user and user.password == password:
        # User authentication successful, set user ID in session
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful.', 'user_id': user.id}), 200
    else:
        # Invalid username or password
        return jsonify({'error': 'Invalid username or password.'}), 401

def logout_user():
    # Check if the user is logged in
    if 'user_id' in session:
        # Remove user ID from the session
        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful.'}), 200
    else:
        # User is not logged in
        return jsonify({'error': 'User is not logged in.'}), 401

@app.route('/api/v1/users/{user_id}/posts', methods=['GET'])
def show_user_posts(user_id):
    user_posts=db.session.execute(db.select(PostTable).filter_by(user_id=user_id)).scalars()
    # Convert the queried posts to a list of dictionaries
    posts_list = []
    for post in user_posts:
        post_dict={
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
    posts_list.append(post_dict)
    return jsonify(post_dict)

@app.route('/api/v1/users/{user_id}/posts', methods=['POST'])
def add_user_post():
    # Extract data from the JSON request sent via Postman
    caption = request.json.get('caption')
    photo = request.json.get('photo')
    user_id = session['user_id']  # Get user ID from the session

    # Create a new post instance
    new_post = PostTable(caption=caption, photo=photo, user_id=user_id)

    # Add the new post to the database session and commit the transaction
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post added successfully.'}), 201

@app.route('/api/users/{user_id}/follow', methods=['POST'])
def create_follow(user_id):
    # Extract data from the JSON request sent via Postman
    target_user_id = request.json.get('target_user_id')
    follower_id = session['user_id']  # Get user ID from the session

    new_follow = FollowTable(follower_id=follower_id, user_id=target_user_id)

    db.session.add(new_follow)
    db.session.commit()

    return jsonify({'message': 'Follow relationship created successfully.'}), 201

@app.route('/api/v1/posts', methods=['GET'])
def show_all_posts():
    user_posts=db.session.execute(db.select(PostTable)).scalars()
    # Convert the queried posts to a list of dictionaries
    posts_list = []
    for post in user_posts:
        post_dict = {
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
        posts_list.append(post_dict)
    return jsonify(posts_list)

@app.route('/api/v1/posts/{post_id}/like', methods=['POST'])
def set_like(post_id):
    # Extract data from the JSON request sent via Postman
    post_id = request.json.get('post_id')
    user_id = session['user_id']  # Get user ID from the session
    new_like = LikeTable(post_id, user_id)
    db.session.add(new_like)
    db.session.commit()
    return render_template('all_posts.html')

###
# Routing for  application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    """Render the website's register page."""
    form = RegisterForm()
    if form.validate_on_submit():
        #id not needed because it auto incremented
        usernameForm = form.username.data
        passwordForm = form.password.data
        firstnameForm= form.firstname.data
        lastnameForm= form.lastname.data
        emailForm= form.email.data
        locationForm= form.location.data
        biographyForm= form.biography.data
        photoForm= form.photo.data
        filename = secure_filename(photoForm.filename)
        photoForm.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        joined_on=datetime.now(timezone.utc)

        new_user=UserProfile(id,usernameForm,passwordForm,firstnameForm,lastnameForm,emailForm,locationForm,biographyForm,filename,joined_on)
        db.session.add(new_user) 
        db.session.commit()
        return redirect(url_for('login.html'))
    return render_template('register.html', form=form)

@app.route('/login',methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usernameForm = form.username.data
        passwordForm = form.password.data

        user=db.session.execute(db.select(UserProfile).filter_by(username=usernameForm)).scalar_one() 
        
        #login_user(user)
        if check_password_hash(user.password,passwordForm):
            # Remember to flash a message to the user
            session['user_id'] = user.id
            flash('You have logged in successfully !!!')
            return redirect(url_for('upload')) # The user should be redirected to the upload form instead
    return render_template("login.html", form=form)

@app.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('Logged out!!!')
    return redirect(url_for('login'))


@app.route('/users/{user_id}', methods=['GET'])
def user_posts(user_id):
    user_posts=db.session.execute(db.select(PostTable).filter_by(user_id=user_id)).scalars()
    # Convert the queried posts to a list of dictionaries
    posts_list = []
    for post in user_posts:
        posts_list.append({
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        })
    #return jsonify(posts_list)
    return render_template('/user_posts.html', posts=posts_list)

@app.route('/posts/new', methods=['POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        #id not needed because it auto incremented
        user_id = session['user_id']
        captionForm=form.caption.data
        photoForm= form.photo.data
        filename = secure_filename(photoForm.filename)
        photoForm.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        created_on=datetime.now(timezone.utc)
        new_post=PostTable(captionForm,filename,user_id,created_on)
        db.session.add(new_post) 
        db.session.commit()
        return redirect(url_for('home.html'))
    return render_template('post.html', form=form)

#@app.route('/<user_id>/follow', methods=['POST'])
def follow(user_id):
     # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User is not logged in.'}), 401
    session_user_id = session['user_id']     #the target user id number must be retrieved
    new_follow = FollowTable(session_user_id, user_id)
    db.session.add(new_follow)
    db.session.commit()
    return render_template('user_posts.html')

@app.route('/posts', methods=['GET'])
def feed():
    user_posts=db.session.execute(db.select(PostTable)).scalars()
    # Convert the queried posts to a list of dictionaries
    posts_list = []
    for post in user_posts:
        posts_list.append({
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        })
    #return jsonify(posts_list)
    return render_template('all_posts.html', posts=posts_list)

#@app.route('/posts/<post_id>/like', methods=['POST'])
def set_like(post_id):
    user_id = session['user_id']     #the user id number must be retrieved
    new_like = LikeTable(post_id, user_id)
    db.session.add(new_like)
    db.session.commit()
    return render_template('all_posts.html')


###
# Functionalities
###

@app.route('/uploads/<filename>', methods=['GET'])
def get_image(filename):
    rootdir=os.getcwd()
    return send_from_directory(os.path.join(os.getcwd(),app.config['UPLOAD_FOLDER']), filename)

#Load Images
def get_uploaded_images():
    rootdir = os.getcwd()
    uploaded_images = []

    for subdir, dirs, files in os.walk(rootdir + '/uploads'):
        for file in files:
            uploaded_images.append(os.path.join(subdir, file).split("\\")[-1])
    return uploaded_images[1:]
    
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
