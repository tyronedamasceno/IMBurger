from datetime import datetime

from flask import current_app
from flask_login import UserMixin

from imburger import db, login_manager


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
        backref='user',
        lazy=True
    )

