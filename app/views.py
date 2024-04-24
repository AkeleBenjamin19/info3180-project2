from datetime import datetime, timezone
import os
import jwt
from app import app, db, login_manager
from flask import jsonify, render_template, request, redirect, url_for, flash, session, abort,send_from_directory, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile,FollowTable,PostTable,LikeTable
from app.forms import LoginForm,PostForm,RegisterForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from flask_wtf.csrf import generate_csrf
from functools import wraps
from datetime import datetime
from werkzeug.datastructures import FileStorage
from sqlalchemy import func, literal_column

###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
 return jsonify({'csrf_token': generate_csrf()})

# Create a JWT @authorize decorator
# This decorator can be used to denote that a specific route should check
# for a valid JWT token before displaying the contents of that route.
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', None) # or request.cookies.get('token', None)

        if not auth:
            return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
        elif len(parts) == 1:
            return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
        elif len(parts) > 2:
            return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

        token = parts[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
        except jwt.DecodeError:
            return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

        g.current_user = user = payload
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/secure/user-info', methods=['GET'])
@authorize
def get_user_info():
    user_id = g.current_user['id']
    return jsonify({'user_id': user_id}), 200

@app.route('/api/v1/register', methods=['POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
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


@app.route('/api/v1/auth/login',methods=['POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']
            
            user = UserProfile.query.filter_by(username=username).first()
            if not user:
                return jsonify({"error": "User does not exist!"}), 404
            
            if not check_password_hash(user.password, password):
                return jsonify({"error": "Invalid credentials!"}), 401
            
            data = {
                "id": user.id,
                "username": user.username
            }
            
            token = jwt.encode(data, app.config["SECRET_KEY"], algorithm="HS256")
            return jsonify({
                "message": "Login was successful",
                "token": token
            })
    else:
        return jsonify({"error": "Invalid request!"}), 400


@app.route('/api/v1/auth/logout', methods=['POST'])
@authorize
def logout():
    return jsonify({"message": "User has been logged out."}), 200

# POST - Used for adding posts to the user's feed
@app.route('/api/v1/users/<user_id>/posts', methods=['POST'])
@authorize
def add_post(user_id):
    # if g.current_user['id'] != user_id:
    #     return jsonify({'error': 'Unauthorized access'}), 403
    
    form = PostForm()
    if form.validate_on_submit():
        caption=form.caption.data
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_post = PostTable(caption=caption, photo=filename, user_id=g.current_user['id'])
        db.session.add(new_post)
        db.session.commit()

        return jsonify({"message": "Post added successfully.", "post_id": new_post.id}), 201
    else:
        print(form_errors(form))
        return jsonify({'errors': form_errors(form)}), 400

# GET - Returns a user's posts
@app.route('/api/v1/users/<user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    posts = PostTable.query.filter_by(user_id=user_id).all()
    posts_data = [{"id": post.id, "caption": post.caption, "photo": post.photo, "created_on": post.created_on} for post in posts]
    return jsonify(posts_data), 200

# POST - Create a Follow relationship between the current user and the target user.
@app.route('/api/users/<user_id>/follow', methods=['POST'])
@authorize
def follow_user(user_id):
    new_follow = FollowTable(follower_id=g.current_user['id'], user_id=user_id)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({"message": "Followed user successfully."}), 201


# GET - Return all posts for all users

@app.route('/api/v1/posts', methods=['GET'])
@authorize
def get_all_posts():
    current_user_id = g.current_user['id']  # Make sure this correctly fetches the user ID

    posts = db.session.query(
        PostTable.id,
        PostTable.caption,
        PostTable.photo.label('post_photo'),
        UserProfile.id.label('user_id'),
        UserProfile.username,
        UserProfile.photo.label('user_photo'),
        db.func.count(LikeTable.id).label('likes'),
        PostTable.created_on,
        db.func.coalesce(db.func.bool_or(LikeTable.user_id == current_user_id), False).label('liked_by_current_user')
    ).join(UserProfile, PostTable.user_id == UserProfile.id) \
     .outerjoin(LikeTable, PostTable.id == LikeTable.post_id) \
     .group_by(PostTable.id, UserProfile.id) \
     .order_by(PostTable.created_on.desc()) \
     .all()

    posts_data = [
        {
            "id": post.id,
            "caption": post.caption,
            "post_photo": f"/api/v1/photos/{post.post_photo}",
            "user_id": post.user_id,
            "username": post.username,
            "user_photo": f"/api/v1/photos/{post.user_photo}",
            "likes": post.likes,
            "liked_by_current_user": post.liked_by_current_user,
            "created_on": post.created_on.strftime("%d %b %Y")
        } for post in posts
    ]
    
    return jsonify(posts_data), 200


# POST - Set a like on the current Post by the logged in User
@app.route('/api/v1/posts/<post_id>/like', methods=['POST'])
@authorize
def like_post(post_id):
    new_like = LikeTable(post_id=post_id, user_id=g.current_user['id'])
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"message": "Post liked successfully."}), 201


@app.route('/api/v1/photos/<filename>', methods=['GET'])
def get_photo(filename):
    rootdir = app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(os.getcwd(), rootdir), filename)   

'''@app.route('/api/v1/users/<user_id>/posts', methods=['POST'])
@authorize
def add_user_post(user_id):
    caption = request.json.get('caption')
    photo = request.json.get('photo')
    user_id = g.current_user...

    # Get the current date and time
    created_on = datetime.now()

    # Create a new post instance with the created_on argument
    new_post = PostTable(caption=caption, photo=photo, user_id=user_id, created_on=created_on)

    # Add the new post to the database session and commit the transaction
    db.session.add(new_post)
    db.session.commit()
 
    return jsonify({'message': 'Post added successfully.'}), 201


@app.route('/api/v1/users/<user_id>/posts', methods=['GET'])
@authorize
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

@app.route('/api/v1/posts', methods=['GET'])
@authorize
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

@app.route('/api/users/<user_id>/follow', methods=['POST'])
@authorize
def create_follow(user_id):
    # Extract data from the JSON request sent via Postman
    target_user_id = request.json.get('target_user_id')
    follower_id = session['user_id']  # Get user ID from the session

    new_follow = FollowTable(follower_id=follower_id, user_id=target_user_id)

    db.session.add(new_follow)
    db.session.commit()

    return jsonify({'message': 'Follow relationship created successfully.'}), 201

@app.route('/api/v1/posts/<post_id>/like', methods=['POST'])
#@authorize
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


@app.route('/users/{user_id}', methods=['GET'])
#@authorize
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
#@authorize
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
#@authorize
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
#@authorize
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
#@authorize
def set_like(post_id):
    user_id = session['user_id']     #the user id number must be retrieved
    new_like = LikeTable(post_id, user_id)
    db.session.add(new_like)
    db.session.commit()
    like_dict={
        'post_id':post_id,
        'user_id':user_id
    }
    return jsonify(like_dict)'''


###
# Functionalities
###
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
