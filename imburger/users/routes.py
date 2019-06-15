from flask import (
    render_template, url_for, flash, redirect, request, Blueprint, session
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
        flash('Você já está logado!', 'warning')
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
        return redirect(url_for('main.home'))

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

            # Com o usuário já logaod, precisamos saber se o usuário é cliente, funcionario ou administrador

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
                session['tipo_usuario'] = 1
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
                    session['tipo_usuario'] = 3
                else:
                    # Caso o empregado seja apenas um funcionario normal, colocamos isso na variavel de sessão
                    session['tipo_usuario'] = 2


            login_user(obj_user, remember=True)

            next_page = request.args.get('next')
            flash(f'Você logou com sucesso!', 'success')
            return (
                redirect(next_page) if next_page
                else redirect(url_for('main.home'))
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
        session['tipo_usuario'] = 0
        logout_user()
        flash('Logout com sucesso!', 'success')
    else:
        flash('Não há usuários logados!', 'warning')
    return redirect(url_for('main.home'))

@users.route("/my_profile", methods=['GET', 'POST'])
@login_required
def my_profile():
    form = forms.UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Sua conta foi atualizada com sucesso', 'success')
        return redirect(url_for('users.my_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('my_profile.html', title='Account',
                           image_file=image_file, form=form)