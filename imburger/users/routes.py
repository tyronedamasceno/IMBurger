from flask import (
    render_template, url_for, flash, redirect, request, Blueprint
)
from flask_login import (
    login_user, current_user, logout_user, login_required
)

from imburger import db, bcrypt
from imburger.models import User, Employee, Customer
from imburger.users import forms


users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'warning')
        return redirect(url_for('main.home'))

    form = forms.RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            given_name=form.given_name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been successfully created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'warning')
        return redirect(url_for('main.index'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You have been logged in!', 'success')
            return (
                redirect(next_page) if next_page
                else redirect(url_for('main.index'))
            )
        else:
            flash(
                'Login Unsucessful. Please check email and password',
                'danger'
            )
    return render_template('login.html', title='login', form=form)

            
