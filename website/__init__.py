from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import json


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'



    # Blueprint setup
    from .auth import auth
    from .pages import pages
    from .learn import learn
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(pages, url_prefix='/')
    app.register_blueprint(learn, url_prefix='/')
    
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


def load_data(file, model):
    with open(file, 'r') as file:
        data = json.load(file)
        
        match model.__name__:
            case "Question":
                for item in data:
                    instance = model(**item, user_id=current_user.id)
                    # check if the model doesnt already exist in the db
                    if not model.query.filter_by(**item, user_id=current_user.id).first():
                        db.session.add(instance)
            case "Lesson"|"Grade"|"Badge":
                for item in data:
                    instance = model(**item)
                    print(instance)
                    # check if the model doesnt already exist in the db
                    if not model.query.filter_by(**item).first():
                        db.session.add(instance)
            case _:
                print("[load_data default] Ceva nu merge")

        try:
            db.session.commit()
        except:
            print("[load_data exception] Nimic de adaugat in baza de date")
            

# TO DO: move this function in another file with utility functions
def populate_db():
    from .models import Grade, Lesson, Question, Badge
    
    load_data('Python/Project0/preload_data/grades.json', Grade)
    load_data('Python/Project0/preload_data/lessons.json', Lesson)
    load_data('unihack-2024/preload_data/questions.json', Question)
    load_data('unihack-2024/preload_data/badges.json', Badge)
    

def create_db(app):
    if not os.path.exists('website/db.sqlite3'):
        with app.app_context():
            db.create_all()