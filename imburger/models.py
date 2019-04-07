from imburger import db

from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100)
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
    password = db.Column(
        db.String(20),
        nullable=False
    )
    picture = db.Column(
        db.String(20),
        nullable=False,
        default='default.jpg'
    )
    customer = db.relationship(
        'Customer',
        backref='user',
        uselist=False
    )
    employee = db.relationship(
        'Employee',
        backref='user',
        uselist=False
    )

    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.picture}")'


class Customer(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )
    promo_points = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    address = db.Column(
        db.String(100),
        nullable=False
    )


class Employee(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )
    registration = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )
    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
