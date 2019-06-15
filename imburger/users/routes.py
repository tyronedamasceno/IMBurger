from flask import (
    render_template, url_for, flash, redirect, request, Blueprint, session
)
from flask_login import (
    login_user, current_user, logout_user, login_required
)

from imburger import db, bcrypt
from imburger.models import User, Employee, Customer
from imburger.users import forms

from imburger.users.utils import save_picture

users = Blueprint('users', __name__)

@users.route("/")
@users.route("/home")
def home():
    if session['user_type'] == 2:
        return redirect(url_for('users.order_management'))
    elif session['user_type'] == 3:
        return redirect(url_for('users.stock_management'))

    return render_template('home.html', home_page=True, title='Inicio')


@users.route("/about")
def about():
    return render_template('about.html', about_page=True, title='Quem Somos')

@users.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        flash('Você já está logado!', 'warning')
        return redirect(url_for('users.home'))

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
            else:
                insert_employee_sql = (
                    'INSERT INTO employee (registration, admin, user_id)'
                    ' VALUES (:registration, :admin, :user_id)'
                )
                conn.execute(
                    insert_employee_sql,
                    registration=registration_number, admin=0 if int(user_type) == 2 else 1,
                    user_id=user_id
                )

            trans.commit()
        except:
            trans.rollback()

        flash('Sua conta foi criada com sucesso!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Você já está logado!', 'warning')
        return redirect(url_for('users.home'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data 
        password = form.password.data

        conn = db.engine.connect()
        select_user_sql = (
            'SELECT * FROM user WHERE email=:email'
        )
        result = conn.execute(
            select_user_sql,
            email=email
        )
        user = result.fetchone()

        if user and bcrypt.check_password_hash(
            user['password'], form.password.data
        ):
            obj_user = User.query.get(user['id'])

            # Com o usuário já logado, precisamos saber se o usuário é cliente, funcionario ou administrador

            user_id = user['id']

            # Minha ideia é: primeiro fazer uma pesquisa na tabela de clientes para ver se encontramos o id do usuario logado lá.

            select_customer_sql = (
            'SELECT * FROM customer WHERE user_id=:user_id'
            )
            result = conn.execute(
                select_customer_sql,
                user_id=user_id
            )

            user = result.fetchone()

            if user:
                # Caso o id do usuario seja encontrado na tabela de clientes, o usuario é cliente e colocamos a variavel na sessão
                session['user_type'] = 1
            else:
                # Caso não, sabemos que o usuario é um funcionario e está na tabela de funcionários, basta saber se é administrador ou nao

                select_employee_sql = (
                'SELECT * FROM employee WHERE user_id=:user_id'
                )
                
                result = conn.execute(
                select_employee_sql,
                user_id=user_id
                )

                user = result.fetchone()
                if user['admin']:
                    # Caso o empregado retornado seja administrador, colocamos isso na variavel de sessão
                    session['user_type'] = 3
                else:
                    # Caso o empregado seja apenas um funcionario normal, colocamos isso na variavel de sessão
                    session['user_type'] = 2


            login_user(obj_user, remember=True)

            next_page = request.args.get('next')
            flash(f'Você logou com sucesso!', 'success')
            return (
                redirect(next_page) if next_page
                else redirect(url_for('users.home')) if session['user_type'] == 1
                else redirect(url_for('users.order_management')) if session['user_type'] == 2
                else redirect(url_for('users.stock_management')) 
            )
        else:
            # Caso não, login mal sucedido
            flash(
                'Login  mal sucedido. Verifique seu email e senha',
                'danger'
            )
    return render_template('login.html', title='login', form=form)


@users.route("/logout")
def logout():
    if current_user.is_authenticated:
        session['user_type'] = 0
        logout_user()
        flash('Logout com sucesso!', 'success')
    else:
        flash('Não há usuários logados!', 'warning')
    return redirect(url_for('users.home'))

@users.route("/my_profile", methods=['GET', 'POST'])
@login_required
def my_profile():
    form = forms.UpdateAccountForm()
    if form.validate_on_submit():

        # Dados para alterar meu perfil \/

        user_id = current_user.id
        image_file = current_user.image_file
        given_name = form.given_name.data
        surname = form.surname.data
        username = form.username.data
        email = form.email.data

        if form.picture.data:
            image_file= save_picture(form.picture.data)

        conn = db.engine.connect()
        trans = conn.begin()

        try:
            update_user_sql = (
                'UPDATE user SET given_name = :given_name, surname = :surname, username = :username, email = :email, image_file = :image_file WHERE id = :user_id'
            )
            conn.execute(
                update_user_sql,
                given_name=given_name, surname=surname, username=username, 
                email=email, image_file=image_file, user_id=user_id
            )

            trans.commit()
        except:
            trans.rollback()

        flash('Sua conta foi atualizada com sucesso', 'success')
        return redirect(url_for('users.my_profile'))
    elif request.method == 'GET':
        form.given_name.data = current_user.given_name
        form.surname.data = current_user.surname
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('my_profile.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/order_management")
@login_required
def order_management():
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))
    return render_template('order_management.html')

@users.route("/stock_management")
@login_required
def stock_management():
    if session['user_type'] != 3:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.order_management'))
    return render_template('stock_management.html')