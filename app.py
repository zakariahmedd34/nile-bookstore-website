from flask import Flask, flash, redirect, url_for  
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Apply test config if provided
    if test_config:
        app.config.update(test_config)
    else:
        
        database_url = os.getenv("DATABASE_URL")

        if database_url:
            # Railway / Production
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        else:
            # Local development
            db_user = os.getenv("MYSQLUSER", "root")
            db_password = os.getenv("MYSQLPASSWORD", "Password@1234#")
            db_host = os.getenv("MYSQLHOST", "localhost")
            db_name = os.getenv("MYSQLDB", "bookstore")

            app.config["SQLALCHEMY_DATABASE_URI"] = (f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}")
            
    # Secret key for sessions
    app.secret_key = os.getenv("SECRET_KEY") or "test-secret-key"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    bcrypt = Bcrypt(app)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        flash("You must login first.", "error")
        return redirect(url_for('login'))
    
    from route import register_routes
    register_routes(app, db, bcrypt)

    migrate = Migrate(app, db)

    return app