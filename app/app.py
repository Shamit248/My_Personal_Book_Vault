from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.extension import bcrypt,login_manager,db,migrate
from flask_migrate import Migrate
from app.blueprints.auth import routes
from dotenv import load_dotenv 
import os

load_dotenv()

def create_app():
    app=Flask(__name__,template_folder="templates",static_folder='static',static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///./test.db'
    app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view="auth.index"
    
    from app.blueprints.auth.modules import Credential
    
    @login_manager.user_loader
    def load_user(pid):
        return Credential.query.get(pid)
    
    #import and register all bluprints
    from app.blueprints.auth.routes import auth
    
    app.register_blueprint(auth,url_prefix='/')
    
    return app
    
    
