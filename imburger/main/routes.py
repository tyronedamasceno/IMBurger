from flask import render_template, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

main = Blueprint('main', __name__)

db = SQLAlchemy()

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html', home_page=True, title='Inicio')


@main.route("/about")
def about():
    return render_template('about.html', about_page=True, title='Quem Somos')
