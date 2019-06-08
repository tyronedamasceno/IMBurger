from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError
)
from flask_login import current_user

from imburger.models import User, Customer, Employee


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=2, max=20)])
    given_name = StringField('Nome', validators=[
        DataRequired(), Length(min=2, max=20)])
    surname = StringField('Sobrenome', validators=[
        DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[
        DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    registration_number = StringField('Matrícula de funcionário', validators=[
        Length(min=2, max=20)])
    street = StringField('Nome da rua', validators=[
        DataRequired(), Length(min=2, max=100)])
    number = StringField('Número', validators=[
        DataRequired(), Length(min=2, max=10)])
    zipcode = StringField('CEP', validators=[
        Length(min=2, max=10)])
    neighborhood = StringField('Bairro', validators=[
        Length(min=2, max=100)])
    city = StringField('Cidade', validators=[
        Length(min=2, max=100)])
    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username has already been used')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email has already been used')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
