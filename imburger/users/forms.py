from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError
)
from flask_login import current_user

from imburger.models import User, Customer, Employee


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu username precisa ter entre 2 e 20 caracteres")])
    given_name = StringField('Nome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu nome precisa ter entre 2 e 20 caracteres")])
    surname = StringField('Sobrenome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu sobrenome precisa ter entre 2 e 20 caracteres")])
    email = StringField('Email', validators=[
        DataRequired(message="Campo obrigatorio"), Email(message="email invalido")])
    password = PasswordField('Password', validators=[DataRequired(message="Campo obrigatorio")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Campo obrigatorio"), EqualTo('password', message="Senhas digitadas não são iguais")])
    registration_number = StringField('Matrícula de funcionário', validators=[
        Length(min=2, max=20, message="Este campo precisa ter entre 2 e 20 caracteres")])
    street = StringField('Nome da rua', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=100, message="Este campo precisa ter entre 2 e 100 caracteres")])
    number = StringField('Número', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=10, message="Este campo precisa ter entre 2 e 10 caracteres")])
    zipcode = StringField('CEP', validators=[
        Length(min=2, max=10, message="Este campo precisa ter entre 2 e 10 caracteres")])
    neighborhood = StringField('Bairro', validators=[
        Length(min=2, max=100, message="Este campo precisa ter entre 2 e 100 caracteres")])
    city = StringField('Cidade', validators=[
        Length(min=2, max=100, message="Este campo precisa ter entre 2 e 100 caracteres")])
    user_type = SelectField('Tipo de Usuario', choices=[("1","Cliente"),("2","Funcionario"),("3","Administrator")], validators=[])
    submit = SubmitField('Criar conta')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este username já está em uso')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está em uso')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Campo obrigatorio"), Email()])
    password = PasswordField('Password', validators=[DataRequired(message="Campo obrigatorio")])
    remember = BooleanField('Lembre-me')
    submit = SubmitField('Login')
