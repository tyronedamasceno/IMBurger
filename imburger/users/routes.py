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

        conn = db.engine.connect()
        trans = conn.begin()
        try:
            insert_user_sql = (
                'INSERT INTO user (username, given_name, surname, email, password, image_file)'
                ' VALUES (:username, :given_name, :surname, :email, :password, :image_file)'
            )
            conn.execute(
                insert_user_sql,
                username=username, given_name=given_name, surname=surname,
                email=email, password=hashed_password, image_file='default.jpg'
            )
            user_id = conn.execute('SELECT * FROM user').lastrowid

            if int(user_type) == 1:
                insert_address_sql = (
                    'INSERT INTO address (street, number, zipcode, neighborhood, city)'
                    ' VALUES (:street, :number, :zipcode, :neighborhood, :city)'
                )
                conn.execute(
                    insert_address_sql,
                    street=street, number=number, zipcode=zipcode,
                    neighborhood=neighborhood, city=city
                )
                address_id = conn.execute('SELECT * FROM address').lastrowid

                insert_customer_sql = (
                    'INSERT INTO customer (promo_points, user_id, address_id)'
                    ' VALUES (:promo_points, :user_id, :address_id)'
                )
                conn.execute(
                    insert_customer_sql,
                    promo_points=0, user_id=user_id, address_id=address_id
                )
            trans.commit()
        except:
            trans.rollback()

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

            
