from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed 
from wtforms import StringField, IntegerField,FileField,TextAreaField,SelectField,PasswordField,DateTimeField
from wtforms.validators import InputRequired,DataRequired
from datetime import datetime,timezone



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class PostForm(FlaskForm):
    photo = FileField('Photo', validators=[
        FileRequired(message="Please select an image."),
        FileAllowed(['jpg', 'jpeg', 'png'], message="Images Only!")
    ])
    caption = TextAreaField('Caption', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    firstname = StringField('Firstname', validators=[InputRequired()])
    lastname = StringField('Lastname', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    biography = TextAreaField('Biography', validators=[InputRequired()])
    photo = FileField('Profile Photo', validators=[
        FileRequired(message="Please select an image."),
        FileAllowed(['jpg', 'jpeg', 'png'], message="Images Only!")
    ])

