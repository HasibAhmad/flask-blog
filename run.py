from flaskblog import app
from flask_sqlalchemy import SQLAlchemy
from flaskblog.models import User
from flaskblog import db

def init_db():
    """
    Populate db and add admin user.
    """
    db.drop_all()
    db.create_all()

    # Create admin user
    admin = User()
    admin.username = 'Hasib'
    admin.email = 'hasib@gmail.com'
    admin.password = '$2b$12$/trVoxWVA6z5JAJ5OiIZSORb1wAMoUdmWSBDGBZtmyvSe6tS.aroi' # password is admin@123
    admin.is_admin = True
    admin.is_blogger = True

    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
    # init_db()
    app.run(debug=True, port=7000)

