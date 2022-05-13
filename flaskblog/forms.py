from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Regexp, Optional
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Length(min=2, max=20),
                               Regexp('^\w+$', message="Username must contain only letters, numbers or underscore"),
                           ])
    email = StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Length(min=8, max=32),
                                 Regexp(".*[a-z].*", message="password should contain lowercase"),
                                 Regexp(".*[A-Z].*", message="password should contain uppercase"),
                                 Regexp(".*[0-9].*", message="password should contain digit"),
                                 Regexp(".*?[!@#\$&*~].*", message="password should contain one symbol at least")
                             ])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[
                                         DataRequired(),
                                         EqualTo('password', message="Confirm Password must be equal to Password")
                                     ])
    is_blogger = BooleanField('I am a blogger')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('username is already taken!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email is already taken!')


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
                               Length(min=2, max=20),
                               Regexp('^\w+$', message="Username must contain only letters, numbers or underscore"),
                           ])
    email = StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()
                        ])
    password = PasswordField('Password')
    new_password = PasswordField('New Password', 
                                    validators=[
                                        Optional(),
                                        Length(min=8, max=32),
                                        Regexp(".*[a-z].*", message="password should contain lowercase"),
                                        Regexp(".*[A-Z].*", message="password should contain uppercase"),
                                        Regexp(".*[0-9].*", message="password should contain digit"),
                                        Regexp(".*?[!@#\$&*~].*", message="password should contain one symbol at least")
                                    ])
    confirm_password = PasswordField('Confirm Password',
                                        validators=[
                                            EqualTo('new_password', message="Confirm Password must be equal to New Password")
                                        ])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
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
    
    def validate_password(self, password):
        if password.data == '' and self.new_password.data != '':
            raise ValidationError('Enter Password also to change password')
        if password.data != '' and self.new_password.data == '':
            raise ValidationError('Enter New Password also to change password or leave Password blank')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100),])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=50),])
    content = CKEditorField('Content', validators=[DataRequired()])
    picture = FileField('Add a picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'jfif'])])
    submit = SubmitField('Post')

class SearchPostForm(FlaskForm):
    search_term = StringField('Search Term', render_kw={"placeholder": "search by title"})