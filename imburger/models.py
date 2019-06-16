from datetime import datetime

from flask_login import UserMixin

from imburger import db


class User(db.Model, UserMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )
    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    given_name = db.Column(
        db.String(20),
        unique=False,
        nullable=False,
    )
    surname = db.Column(
        db.String(20),
        unique=False,
        nullable=False,
    )
    image_file = db.Column(
        db.String(20),
        nullable=False,
        default='default.jpg'
    )
    password = db.Column(
        db.String(60),
        nullable=False
    )
    employee = db.relationship(
        'Employee',
        backref='user',
        lazy=True
    )
    customer = db.relationship(
        'Customer',
        backref='user',
        lazy=True
    )


class Employee(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    registration = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )
    admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )


class Customer(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    promo_points = db.Column(
        db.Integer,
        default=0,
        unique=False,
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
    address_id = db.Column(
        db.Integer,
        db.ForeignKey('address.id'),
        nullable=True
    )
    order = db.relationship(
        'Order',
        backref='customer',
        lazy=True
    )


class Address(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    street = db.Column(
        db.String(100),
        unique=False,
        nullable=False
    )
    number = db.Column(
        db.String(10),
        unique=False,
        nullable=False
    )
    zipcode = db.Column(
        db.String(10),
        unique=False,
        nullable=True
    )
    neighborhood = db.Column(
        db.String(100),
        unique=False,
        nullable=True
    )
    city = db.Column(
        db.String(100),
        unique=False,
        nullable=True
    )
    customer = db.relationship(
        'Customer',
        backref='address',
        lazy=True
    )


class Order(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    # 0 = Preparing
    # 1 = Delivering
    # 2 = Cancelled
    # 3 = Finished
    status = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customer.id'),
        nullable=False
    )


class Product(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(50),
        unique=False,
        nullable=False
    )
    price = db.Column(
        db.Float,
        nullable=False,
        default=0
    )
    description = db.Column(
        db.String(100),
        unique=False,
        nullable=True
    )


class Ingredient(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(50),
        unique=False,
        nullable=False
    )
    unit_measuring = db.Column(
        db.String(50),
        unique=False,
        nullable=False
    )
    stock = db.relationship(
        'Stock',
        backref='ingredient',
        lazy=True
    )


class Stock(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    quantity = db.Column(
        db.Float,
        nullable=False,
        default=0
    )
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey('ingredient.id'),
        nullable=False
    )


products_ingredients = db.Table(
    'products_ingredients',
    db.Column(
        'product_id',
        db.Integer,
        db.ForeignKey('product.id'),
        primary_key=True
    ),
    db.Column(
        'ingredient_id',
        db.Integer,
        db.ForeignKey('ingredient.id'),
        primary_key=True
    ),
    db.Column(
        'quantity',
        db.Float,
        nullable=False,
        default=1
    )
)

order_products = db.Table(
    'order_products',
    db.Column(
        'product_id',
        db.Integer,
        db.ForeignKey('product.id'),
        primary_key=True
    ),
    db.Column(
        'order_id',
        db.Integer,
        db.ForeignKey('order.id'),
        primary_key=True
    ),
    db.Column(
        'quantity',
        db.Integer,
        nullable=False,
        default=1
    ),
    db.Column(
        'notes',
        db.String(100),
        nullable=True
    )
)
