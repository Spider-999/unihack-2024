from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



    # Blueprint setup
    from .auth import auth
    from .pages import pages
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(pages, url_prefix='/')
    
    # Database setup
    from .models import User
    db.init_app(app)
    migrate.init_app(app, db)
    create_db(app)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app=app)
    login_manager.login_message = "Inregistreaza-te sau autentifica-te pentru a vizualiza site-ul"

    # Tell flask how to load a user, what user to look for
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_db(app):
    if not os.path.exists('website/db.sqlite3'):
        with app.app_context():
            db.create_all()