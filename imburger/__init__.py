import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('DB_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imburger.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from imburger.accounts.routes import accounts as accounts_bp
from imburger.orders.routes import orders as orders_bp
from imburger.main.routes import main as main_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(main_bp)
