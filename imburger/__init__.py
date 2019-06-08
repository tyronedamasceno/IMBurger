from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from imburger.config import Config


app.config.from_object(Config)
app = Flask(__name__)

db = SQLAlchemy(app)
db.drop_all()
db.create_all()

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail(app)

from imburger.users.routes import users as users_bp
from imburger.main.routes import main as main_bp
from imburger.errors.handlers import errors as errors_bp

app.register_blueprint(users_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(main_bp)
