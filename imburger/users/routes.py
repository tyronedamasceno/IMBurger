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

    conn = db.engine.connect()

    select_products_sql = ('SELECT * FROM product')
    result = conn.execute(select_products_sql)

    return render_template('home.html', home_page=True, title='Inicio',  products_homes = result)


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
            flash('Ocorreu uma falha durante a transação!', 'warning')

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
            flash('Ocorreu uma falha durante a transação!', 'warning')

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


@users.route("/product_management")
@login_required
def product_management():
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    conn = db.engine.connect()

    select_products_sql = (
        'SELECT * FROM product'
    )
    result = conn.execute(
        select_products_sql
    )

    return render_template('product_management.html', product_items = result)

@users.route("/product_management/add", methods=['GET', 'POST'])
@login_required
def add_product():
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    form = forms.AddProductForm()

    if form.validate_on_submit():
        # Dados para inserção do novo ingrediente e do novo estoque \/
        name = form.name.data
        price = form.price.data
        description = form.description.data

        conn = db.engine.connect()
        trans = conn.begin()

        try:
            insert_product_sql = (
                'INSERT INTO product (name, price, description)'
                ' VALUES (:name, :price, :description)'
            )
            conn.execute(
                insert_product_sql,
                name=name, price=price, description=description
            )

            trans.commit()
        except:
            trans.rollback()
            flash('Ocorreu uma falha durante a transação!', 'warning')
        return redirect(url_for('users.product_management'))
    
    return render_template('add_product.html', form=form)

@users.route("/product_management/<int:product_id>", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))
    

    conn = db.engine.connect()

    select_product_item_sql = (
        'SELECT * FROM product WHERE id = :product_id'
    )
    result = conn.execute(
        select_product_item_sql,
        product_id=product_id
    )

    product_item = result.fetchone()

    form = forms.AddProductForm()

    if form.validate_on_submit():

        name = form.name.data
        price = form.price.data 
        description = form.description.data

        update_product_sql = (
            'UPDATE product SET name=:name, price=:price, description=:description WHERE id = :product_id'
        )
        conn.execute(
            update_product_sql,
            name=name, price=price, description=description,
            product_id=product_id
        )
            
        return redirect(url_for('users.product_management'))
    elif request.method == 'GET':
        form.name.data = product_item['name']
        form.price.data = product_item['price']
        form.description.data = product_item['description']
    return render_template('product_management_edit.html', form=form, product_item=product_item)

@users.route("/product_management/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))


    conn = db.engine.connect()
    trans = conn.begin()

    try:
        delete_product_ingredients_sql = (
            'DELETE FROM products_ingredients WHERE product_id = :product_id'
        )
        conn.execute(
            delete_product_ingredients_sql,
            product_id=product_id
        )

        delete_product_sql = (
            'DELETE FROM product WHERE id = :product_id'
        )
        conn.execute(
            delete_product_sql,
            product_id=product_id
        )

        trans.commit()
    except:
        trans.rollback()
        flash('Ocorreu uma falha durante a transação!', 'warning')

    return redirect(url_for('users.product_management'))

@users.route("/product_management/add_ingredient/<int:product_id>", methods=['GET', 'POST'])
@login_required
def add_product_ingredient(product_id):
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    conn = db.engine.connect()

    select_product_name_sql = (
        'SELECT id, name FROM product WHERE product.id=:product_id'
    )
    result = conn.execute(
        select_product_name_sql,
        product_id=product_id
    )

    product = result.fetchone()

    select_product_ingredients_sql = (
        'SELECT ingredient.name,products_ingredients.quantity,products_ingredients.product_id,products_ingredients.ingredient_id, ingredient.unit_measuring FROM products_ingredients INNER JOIN ingredient ON products_ingredients.ingredient_id=ingredient.id WHERE products_ingredients.product_id=:product_id;'
    )
    result = conn.execute(
        select_product_ingredients_sql,
        product_id=product_id
    )

    product_ingredients = result

    select_ingredients_sql = (
        'SELECT * from ingredient'
    )
    result = conn.execute(
        select_ingredients_sql
    )

    ingredient_items = result

    form = forms.AddProductIngredientForm()

    form.ingredient_id.choices = []       

    for ingredient_item in ingredient_items:
        form.ingredient_id.choices += [(ingredient_item['id'], ingredient_item['name'])]

    if form.validate_on_submit():
        product_id=product_id
        ingredient_id=form.ingredient_id.data 
        quantity=form.quantity.data

        # Veficiar se já existe uma linha na tabela com o produto-ingrediente:

        search_product_ingredient_sql = (
        'SELECT * FROM products_ingredients WHERE product_id = :product_id AND ingredient_id = :ingredient_id'
        )
        result = conn.execute(
            search_product_ingredient_sql,
            product_id=product_id, ingredient_id=ingredient_id,
        )

        product_ingredient = result.fetchone()

        # Caso já exista, atualizar a linha
        if product_ingredient:
            update_product_ingredient_sql = (
            'UPDATE products_ingredients SET quantity = quantity + :quantity WHERE product_id=:product_id AND ingredient_id=:ingredient_id'
            )
            result = conn.execute(
                update_product_ingredient_sql,
                product_id=product_id, ingredient_id=ingredient_id,
                quantity=quantity
            )
            return redirect(url_for('users.add_product_ingredient', product_id=product_id))
        else:
            insert_product_ingredient_sql = (
            'INSERT INTO products_ingredients (product_id, ingredient_id, quantity)'
            ' VALUES (:product_id, :ingredient_id, :quantity)'
            )
            result = conn.execute(
                insert_product_ingredient_sql,
                product_id=product_id, ingredient_id=ingredient_id,
                quantity=quantity
            )
            return redirect(url_for('users.add_product_ingredient', product_id=product_id))


    return render_template('add_product_ingredient.html', product_ingredients=product_ingredients, ingredient_items=ingredient_items, product=product, form=form)

@users.route("/product_management/product_ingredient/<int:product_id>/<int:ingredient_id>/delete", methods=['POST'])
@login_required
def delete_product_ingredient(product_id, ingredient_id):
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    conn = db.engine.connect()
    trans = conn.begin()

    try:
        delete_product_ingredient_sql = (
            'DELETE FROM products_ingredients WHERE product_id = :product_id AND ingredient_id = :ingredient_id'
        )
        conn.execute(
            delete_product_ingredient_sql,
            product_id=product_id,
            ingredient_id=ingredient_id
        )

        trans.commit()
    except:
        trans.rollback()
        flash('Ocorreu uma falha durante a transação!', 'warning')

    return redirect(url_for('users.add_product_ingredient', product_id=product_id))

@users.route("/order_management")
@login_required
def order_management():
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    conn = db.engine.connect()

    select_order_list_sql = (
        'SELECT "order".id AS "order_id", customer.id AS "customer_id", user.username, "order".status FROM "order" INNER JOIN customer ON "order".customer_id = customer.id INNER JOIN user ON customer.user_id = user.id'
    )
    result = conn.execute(
        select_order_list_sql
    )

    order_list = result

    return render_template('order_management.html', order_list = order_list)

@users.route("/order_management/<int:order_id>", methods=['GET', 'POST'])
@login_required
def order_item_management(order_id):
    if session['user_type'] != 2:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.stock_management'))

    conn = db.engine.connect()

    select_order_item_sql = (
        'SELECT order_products.order_id, "order".status, product.name, product.price, order_products.quantity, order_products.notes FROM order_products INNER JOIN product ON order_products.product_id = product.id INNER JOIN "order" ON order_products.order_id = "order".id WHERE order_products.order_id=1;'
    )
    result = conn.execute(
        select_order_item_sql
    )

    order_item = result.fetchall()

    status = order_item[0]['status']

    form = forms.UpdateOrderStatusForm()

    if form.validate_on_submit():

        order_status = form.order_status.data 

        update_order_item_sql = (
            'UPDATE "order" SET status=:order_status WHERE id = :order_id'
        )
        conn.execute(
            update_order_item_sql,
            order_status=order_status, order_id=order_id
        )
            
        return redirect(url_for('users.order_management'))
    elif request.method == 'GET':
        form.order_status.data = status

    return render_template('order_item_management.html', form=form, order_item=order_item)

@users.route("/stock_management")
@login_required
def stock_management():
    if session['user_type'] != 3:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.order_management'))
    
    conn = db.engine.connect()

    select_stock_items_sql = (
        'SELECT ingredient.name, stock.id, stock.quantity, ingredient.unit_measuring FROM ingredient JOIN stock ON ingredient.id = stock.ingredient_id'
    )
    result = conn.execute(
        select_stock_items_sql
    )

    return render_template('stock_management.html', stock_items = result)

@users.route("/stock_management/<int:stock_id>", methods=['GET', 'POST'])
@login_required
def edit_stock(stock_id):
    if session['user_type'] != 3:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.order_management'))
    

    conn = db.engine.connect()

    select_stock_item_sql = (
        'SELECT ingredient.id AS ingredient_id, ingredient.name, stock.id AS stock_id, stock.quantity, ingredient.unit_measuring FROM ingredient JOIN stock ON ingredient.id = stock.ingredient_id WHERE stock.id = :stock_id'
    )
    result = conn.execute(
        select_stock_item_sql,
        stock_id = stock_id
    )

    stock_item = result.fetchone()
    conn.close()

    form = forms.EditStockForm()

    if form.validate_on_submit():
        quantity = form.quantity.data
        name = form.name.data
        unit_measuring = form.unit_measuring.data

        conn = db.engine.connect()
        trans = conn.begin()

        try:
            update_stock_sql = (
                'UPDATE stock SET quantity = :quantity WHERE id = :stock_id'
            )
            conn.execute(
                update_stock_sql,
                quantity=quantity, stock_id=stock_id
            )

            update_stock_sql = (
                'UPDATE ingredient SET name = :name, unit_measuring = :unit_measuring WHERE id = :ingredient_id'
            )
            conn.execute(
                update_stock_sql,
                name=name, unit_measuring=unit_measuring,
                ingredient_id=stock_item['ingredient_id']
            )
            trans.commit()
        except:
            trans.rollback()
            flash('Ocorreu uma falha durante a transação!', 'warning')

        return redirect(url_for('users.stock_management'))
    elif request.method == 'GET':
        form.name.data = stock_item['name']
        form.quantity.data = stock_item['quantity']
        form.unit_measuring.data = stock_item['unit_measuring']
    return render_template('stock_management_edit.html', form=form, stock_item=stock_item)


@users.route("/stock_management/add", methods=['GET', 'POST'])
@login_required
def add_ingredient():
    if session['user_type'] != 3:
        if session['user_type'] == 1:
            return redirect(url_for('users.home'))
        else:
            return redirect(url_for('users.order_management'))

    form = forms.AddIngredientForm()

    if form.validate_on_submit():
        # Dados para inserção do novo ingrediente e do novo estoque \/
        name = form.name.data
        unit_measuring = form.unit_measuring.data
        initial_quantity = form.initial_quantity.data

        conn = db.engine.connect()
        trans = conn.begin()

        try:
            insert_ingredient_sql = (
                'INSERT INTO ingredient (name, unit_measuring)'
                ' VALUES (:name, :unit_measuring)'
            )
            conn.execute(
                insert_ingredient_sql,
                name=name, unit_measuring=unit_measuring
            )

            ingredient_id = conn.execute('SELECT * FROM ingredient').lastrowid

            insert_stock_sql = (
                'INSERT INTO stock (quantity, ingredient_id)'
                ' VALUES (:quantity, :ingredient_id)'
            )
            conn.execute(
                insert_stock_sql,
                quantity=initial_quantity, ingredient_id=ingredient_id
            )

            trans.commit()
        except:
            trans.rollback()
            flash('Ocorreu uma falha durante a transação!', 'warning')
        return redirect(url_for('users.stock_management'))
    return render_template('add_ingredient.html', form=form)