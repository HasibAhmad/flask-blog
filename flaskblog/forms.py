from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Length(min=2, max=20)
                           ])
    email = StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired()
                             ])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[
                                         DataRequired(),
                                         EqualTo('password')
                                     ])
    is_blogger = BooleanField('I am a blogger')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('username already take!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already take!')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired()
                             ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Length(min=2, max=20)
                           ])
    email = StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    password = PasswordField('Password')
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password')
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('username already take!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('email already take!')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('add a picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')
