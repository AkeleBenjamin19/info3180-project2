from datetime import datetime, timezone
import os
import jwt
from app import app, db, login_manager
from flask import jsonify, request, g, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile, FollowTable, PostTable, LikeTable
from app.forms import LoginForm, PostForm, RegisterForm
from werkzeug.security import check_password_hash
from flask_wtf.csrf import generate_csrf
from functools import wraps
from sqlalchemy import func
from werkzeug.datastructures import FileStorage

# Function to generate CSRF token
@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()})


# Create a JWT authorize decorator
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization', None)

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
            return jsonify({'code': 'token_expired', 'description': 'Token is expired'}), 401
        except jwt.DecodeError:
            return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

        g.current_user = user = payload
        return f(*args, **kwargs)
    return decorated_function


# Route to get user info securely
@app.route('/api/v1/secure/user-info', methods=['GET'])
@authorize
def get_user_info():
    user_id = g.current_user['id']
    return jsonify({'user_id': user_id}), 200


# Route for user registration
@app.route('/api/v1/register', methods=['POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Extract user data from the form
            username = form.username.data
            password = form.password.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            email = form.email.data
            location = form.location.data
            biography = form.biography.data
            photo = form.photo.data

            # Save photo to uploads folder
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a new user profile instance
            new_user = UserProfile(
                username=username,
                password=password,
                firstname=firstname,
                lastname=lastname,
                email=email,
                location=location,
                biography=biography,
                photo=filename
            )

            # Add the new user to the database session and commit
            db.session.add(new_user)
            db.session.commit()

            # Return user data in response
            return jsonify({
                "message": "User Successfully registered",
                'username': new_user.username,
                'password': new_user.password,
                'firstname': new_user.firstname,
                'lastname': new_user.lastname,
                'email': new_user.email,
                'location': new_user.location,
                'biography': new_user.biography,
                'photo': new_user.photo
            }), 200
        return jsonify({"errors": form_errors(form)}), 400

    return jsonify({"error": "Invalid request!"}), 400


# Route for user login
@app.route('/api/v1/auth/login', methods=['POST'])
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


# Route for user logout
@app.route('/api/v1/auth/logout', methods=['POST'])
@authorize
def logout():
    return jsonify({"message": "User has been logged out."}), 200


# Route to add a post to user's feed
@app.route('/api/v1/users/<user_id>/posts', methods=['POST'])
@login_required
def add_post(user_id):
    form = PostForm()
    if form.validate_on_submit():
        # Extract post data from the form
        caption = form.caption.data
        photo = form.photo.data

        # Save photo to uploads folder
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Create a new post instance
        new_post = PostTable(caption=caption, photo=filename, user_id=current_user.id)

        # Add the new post to the database session and commit
        db.session.add(new_post)
        db.session.commit()

        # Return success message
        return jsonify({"message": "Post added successfully.", "post_id": new_post.id}), 201
    else:
        return jsonify({'errors': form_errors(form)}), 400


# Route to get user's posts
@app.route('/api/v1/users/<user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    posts = PostTable.query.filter_by(user_id=user_id).all()
    posts_data = [{"id": post.id, "caption": post.caption, "photo": post.photo, "created_on": post.created_on} for post in posts]
    return jsonify(posts_data), 200


# Route to follow a user
@app.route('/api/users/<user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    new_follow = FollowTable(follower_id=current_user.id, user_id=user_id)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({"message": "Followed user successfully."}), 201


# Route to get all posts
@app.route('/api/v1/posts', methods=['GET'])
def get_all_posts():
    posts = db.session.query(
        PostTable.id,
        PostTable.caption,
        PostTable.photo.label('post_photo'),
        UserProfile.id.label('user_id'),
        UserProfile.username,
        UserProfile.photo.label('user_photo'),
        db.func.count(LikeTable.id).label('likes'),
        PostTable.created_on,
        db.func.coalesce(db.func.bool_or(LikeTable.user_id == current_user.id), False).label('liked_by_current_user')
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


# Route to set a like on a post
@app.route('/api/v1/posts/<post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    new_like = LikeTable(post_id=post_id, user_id=current_user.id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"message": "Post liked successfully."}), 201


# Route to serve photo files
@app.route('/api/v1/photos/<filename>', methods=['GET'])
def get_photo(filename):
    rootdir = app.config['UPLOAD_FOLDER']
    return send_from_directory(os.path.join(os.getcwd(), rootdir), filename)   


# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': 'Not Found'}), 404


# Here we define a function to collect form errors from Flask-WTF
def form_errors(form):
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages
