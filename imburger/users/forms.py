from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectField, FloatField
from wtforms.validators import (
    DataRequired, InputRequired, Length, Email, EqualTo, ValidationError, NumberRange
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
        DataRequired(message="Campo obrigatorio"), Email(message="endereço de email invalido")])
    password = PasswordField('Senha', validators=[DataRequired(message="Campo obrigatorio")])
    submit = SubmitField('Entrar')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu username precisa ter entre 2 e 20 caracteres")])
    given_name = StringField('Nome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu nome precisa ter entre 2 e 20 caracteres")])
    surname = StringField('Sobrenome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=20, message="Seu sobrenome precisa ter entre 2 e 20 caracteres")])
    email = StringField('Email', validators=[
        DataRequired(message="Campo obrigatorio"), Email(message="email invalido")])
    picture = FileField('Atualizar foto de perfil', validators=[FileAllowed(['jpg', 'png'])])

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Esta username já está em uso. Escolha uma diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email já está em uso. Escolha um diferente.')


class EditStockForm(FlaskForm):
    name = StringField('Nome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=50, message="O nome do ingrediente deve ter entre 2 e 50 caracteres")])
    quantity = FloatField('Quantidade', validators=[
        InputRequired(message="Campo obrigatorio"), NumberRange(min=0.0, message="A quantidade não pode ser negativa")])
    unit_measuring = StringField('Unidade de medida', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=1, max=2, message="A unidade de medida deve ter de 1 a 2 caracteres")])

class AddIngredientForm(FlaskForm):
    name = StringField('Nome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=50, message="O nome do ingrediente deve ter entre 2 e 50 caracteres")])
    initial_quantity = FloatField('Quantidade', validators=[
        InputRequired(message="Campo obrigatorio"), NumberRange(min=0.0, message="A quantidade não pode ser negativa")])
    unit_measuring = StringField('Unidade de medida', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=1, max=2, message="A unidade de medida deve ter de 1 a 2 caracteres")])

class AddProductForm(FlaskForm):
    name = StringField('Nome', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=2, max=50, message="O nome do produto deve ter entre 2 e 50 caracteres")])
    description = TextAreaField('Descrição', validators=[
        DataRequired(message="Campo obrigatorio"), Length(min=3, max=100, message="A descrição deve conter entre 3 a 100 caracteres")])
    price = FloatField('Preço (em reais)', validators=[
        InputRequired(message="Campo obrigatorio"), NumberRange(min=0.0, message="O preço não pode ser negativo")])

class AddProductIngredientForm(FlaskForm):
    ingredient_id = SelectField('Novo ingrediente', coerce=int, choices=[])
    quantity = FloatField('Quantidade', validators=[
        InputRequired(message="Campo obrigatorio"), NumberRange(min=0.0, message="A quantidade não pode ser negativa")])