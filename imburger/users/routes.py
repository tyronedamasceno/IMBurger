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
        print ("==============TESTING BEGING ==============")
        print (form.user_type.data)
        print ("==============TESTING ENDING ==============")
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        # dados para criação do usuario \/

        given_name=form.given_name.data
        surname=form.surname.data
        username=form.username.data
        email=form.email.data
        password=hashed_password
        street=form.street.data
        number=form.number.data
        zipcode=form.zipcode.data
        neighborhood=form.neighborhood.data
        city=form.city.data
        registration_number=form.registration_number.data
        user_type=form.user_type.data # 1 = Cliente / 2 = Funcionario / 3 = Administrador

        # db.session.add(user)
        db.session.commit()
        flash('Your account has been successfully created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Você já está logado!', 'warning')
        return redirect(url_for('main.index'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Você logou com sucesso!', 'success')
            return (
                redirect(next_page) if next_page
                else redirect(url_for('main.index'))
            )
        else:
            flash(
                'Login  malsucedido. Verifique seu email e senha',
                'danger'
            )
    return render_template('login.html', title='login', form=form)

            
