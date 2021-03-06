from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from imburger.config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
from imburger import models
#db.drop_all()
#db.create_all()

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from imburger.models import User
    return User.query.get(user_id)

mail = Mail(app)

from imburger.users.routes import users as users_bp
from imburger.errors.handlers import errors as errors_bp

app.register_blueprint(users_bp)
app.register_blueprint(errors_bp)
