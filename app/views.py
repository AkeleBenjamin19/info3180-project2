from datetime import datetime, timezone
import os
import jwt
from app import app, db, login_manager
from flask import jsonify, render_template, request, redirect, url_for, flash, session, abort,send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile,FollowTable,PostTable,LikeTable
from app.forms import LoginForm,PostForm,RegisterForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from flask_wtf.csrf import generate_csrf
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
 return jsonify({'csrf_token': generate_csrf()})


###
# Routing for postman 
###

@app.route('/api/v1/test', methods=['GET'])
def test():
    alist=["This","is","a","test"]
    return jsonify({'test': 'Testing'}), 200

@app.route('/api/v1/register', methods=['POST'])
def register():
    """Render the website's register page."""
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #id not needed because it auto incremented
            username = form.username.data
            password = form.password.data
            firstname= form.firstname.data
            lastname= form.lastname.data
            email= form.email.data
            location= form.location.data
            biography= form.biography.data
            photo= form.photo.data
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_user=UserProfile(username=username,password=password,firstname=firstname,lastname=lastname,email=email,location=location,biography=biography,photo=filename)
            db.session.add(new_user) 
            db.session.commit()

            return jsonify({
                "message":"User Successfully registered", 
                'username':new_user.username,
                'password': new_user.password,
                'firstname':new_user.firstname,
                'lastname':new_user.lastname,
                'email':new_user.email,
                'location':new_user.location,
                'biography':new_user.biography,
                'photo':new_user.photo
                }),200
        return jsonify({"errors":form_errors(form)}),400

"""@app.route('register', methods=['POST'])
def register_user():
    username = request.json.get('username')
    password = request.json.get('password')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    email = request.json.get('email')
    location = request.json.get('location')
    biography = request.json.get('biography')
    filename = request.json.get('profile_photo')
    joined_on = datetime.now(timezone.utc)
    
    # Check if the username or email already exists in the database
    existing_user = db.session.query(UserProfile).filter(or_(UserProfile.username == username, UserProfile.email == email)).scalar()
    if existing_user:
        return jsonify({'error': 'Username or email already exists.'}), 400
    
    new_user = UserProfile(username, password, firstname, lastname, email, location, biography, filename, joined_on)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully.'}), 201"""


@app.route('/api/v1/auth/login',methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user=db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar_one() 
        
        # Remember to flash a message to the user
        if check_password_hash(user.password, password):
        # Generate JWT token
            access_token = create_access_token(identity=user.id)
            return jsonify({"message": f"{user.username} successfully logged in!!"},access_token=access_token), 200
    else:
        # Invalid credentials
        errors = form_errors(form)
        return jsonify({"errors": errors}), 400

"""@app.route('/api/v1/auth/login', methods=['POST'])
def login_user():
    username = request.json.get('username')
    password = request.json.get('password')


    user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar_one()
    if user is not None and check_password_hash(user.password, password):   
        # User authentication successful, set user ID in session
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful.', 'user_id': user.id}), 200
    else:
        # Invalid username or password
        return jsonify({'error': 'Invalid username or password.'}), 401"""



"""def logout_user():
    # Check if the user is logged in
    if 'user_id' in session:
        # Remove user ID from the session
        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful.'}), 200
    else:
        # User is not logged in
        return jsonify({'error': 'User is not logged in.'}), 401"""

@app.route('/api/v1/users/<user_id>/posts', methods=['GET'])
def show_user_posts(user_id):
    user_posts = db.session.execute(db.select(PostTable).filter_by(user_id=user_id)).scalars()
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


from datetime import datetime

@app.route('/api/v1/users/<user_id>/posts', methods=['POST'])
def add_user_post(user_id):
    # Extract data from the JSON request sent via Postman
    caption = request.json.get('caption')
    photo = request.json.get('photo')
    user_id = session['user_id']  # Get user ID from the session

    # Get the current date and time
    created_on = datetime.now()

    # Create a new post instance with the created_on argument
    new_post = PostTable(caption=caption, photo=photo, user_id=user_id, created_on=created_on)

    # Add the new post to the database session and commit the transaction
    db.session.add(new_post)
    db.session.commit()
 
    return jsonify({'message': 'Post added successfully.'}), 201


@app.route('/api/users/<user_id>/follow', methods=['POST'])
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

@app.route('/api/v1/posts/<post_id>/like', methods=['POST'])
def set_like(post_id):
    # Extract data from the JSON request sent via Postman
    post_id = request.json.get('post_id')
    user_id = session['user_id']  # Get user ID from the session
    new_like = LikeTable(post_id, user_id)
    db.session.add(new_like)
    db.session.commit()
    like_dict={
        'post_id':post_id,
        'user_id':user_id
    }
    return jsonify(like_dict)

###
# Routing for  application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id', None)
    if 'user_id' in session:
        # Remove user ID from the session
        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful.'}), 200
    else:
        return jsonify({'error': 'User is not logged in.'}), 401


@app.route('/users/{user_id}', methods=['GET'])
def user_posts(user_id):
    user_posts=db.session.execute(db.select(PostTable).filter_by(user_id=user_id)).scalars()
    # Convert the queried posts to a list of dictionaries
    for post in user_posts:
        posts_dict={
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
    return jsonify(posts_dict)

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

        posts_dict={
            'id': new_post.id,
            'caption': new_post.caption,
            'photo': new_post.photo,
            'user_id': new_post.user_id,
            'created_on': new_post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
        return jsonify(posts_dict)
    else:
            errors = form_errors(form)
            return jsonify({"errors": errors}), 400

#@app.route('/<user_id>/follow', methods=['POST'])
def follow(user_id):
     # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User is not logged in.'}), 401
    session_user_id = session['user_id']     #the target user id number must be retrieved
    new_follow = FollowTable(session_user_id, user_id)
    db.session.add(new_follow)
    db.session.commit()

    follow_dict={
            'id': new_follow.id,
            'post_id': new_follow.follower_id,
            'user_id': new_follow.user_id,
        }
    return jsonify(follow_dict)

@app.route('/posts', methods=['GET'])
def feed():
    user_posts=db.session.execute(db.select(PostTable)).scalars()
    # Convert the queried posts to a list of dictionaries
    for post in user_posts:
        posts_dict={
            'id': post.id,
            'caption': post.caption,
            'photo': post.photo,
            'user_id': post.user_id,
            'created_on': post.created_on.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime as string
        }
    return jsonify(posts_dict)

#@app.route('/posts/<post_id>/like', methods=['POST'])
def set_like(post_id):
    user_id = session['user_id']     #the user id number must be retrieved
    new_like = LikeTable(post_id, user_id)
    db.session.add(new_like)
    db.session.commit()
    like_dict={
        'post_id':post_id,
        'user_id':user_id
    }
    return jsonify(like_dict)


###
# Functionalities
###
@app.route('/api/v1/photo/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

#Load Images
def get_uploaded_images():
    import os
    rootdir = os.getcwd()
    fileslst = []
    for subdir, dirs, files in os.walk(rootdir + '/uploads'):
        for file in files:
            fileslst.append(file)
    return fileslst

###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
     return jsonify({'error': 'Not Found'}), 404
