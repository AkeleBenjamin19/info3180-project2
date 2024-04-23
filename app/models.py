from . import db
from werkzeug.security import generate_password_hash
from datetime import datetime


class UserProfile(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80),unique=True)
    password= db.Column(db.Text)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    location = db.Column(db.String(255))
    biography = db.Column(db.Text)
    photo = db.Column(db.String(255))
    joined_on = db.Column(db.DateTime, default=datetime.now())
    

    def __init__(self,username,password,firstname,lastname,email,location,biography,photo):
        self.username=username
        self.password = generate_password_hash(password)
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.location = location
        self.biography = biography
        self.photo=photo
        

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.username)

class FollowTable(db.Model):
    __tablename__ = 'Follows'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id=db.Column(db.Integer)
    user_id=db.Column(db.Integer)
    

    def __init__(self,follower_id,user_id):
        self.follower_id=follower_id
        self.user_id = user_id

class LikeTable(db.Model):
    __tablename__ = 'Likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id=db.Column(db.Integer)
    user_id=db.Column(db.Integer)
    

    def __init__(self,post_id,user_id):
        self.post_id=post_id
        self.user_id = user_id

class PostTable(db.Model):
    __tablename__ = 'Posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption= db.Column(db.String(255))
    photo= db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=datetime.now())
    

    def __init__(self,caption,photo,user_id):
        self.caption=caption
        self.photo=photo
        self.user_id = user_id
