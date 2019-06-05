from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from imburger import db, bcrypt

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html', title='Registrar Conta')


@users.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Fazer Login')