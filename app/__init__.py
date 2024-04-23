from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
jwt = JWTManager(app)


db = SQLAlchemy(app)
migrate=Migrate(app,db)
# Instantiate Flask-Migrate library here

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, models
