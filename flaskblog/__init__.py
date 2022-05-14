from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '3bc48d4ca9483b6d0337a8857f6ac1db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Hkhaliqi\\Desktop\\Flask_blog\\blogHub.db'
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_CODE_THEME'] = 'monokai_sublime'	
app.config['CKEDITOR_EXTRA_PLUGINS '] = ['codesnippetgeshi']	
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes