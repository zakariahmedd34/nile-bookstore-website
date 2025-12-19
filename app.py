from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__, template_folder='templates', static_folder='static')

    # =========================
    # CONFIG
    # =========================
    if test_config:
        app.config.update(test_config)
    else:
        database_url = os.getenv("DATABASE_URL")

        if database_url:
            # Railway gives mysql:// but SQLAlchemy needs mysql+pymysql://
            if database_url.startswith("mysql://"):
                database_url = database_url.replace(
                    "mysql://", "mysql+pymysql://", 1
                )

            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        else:
            # Local MySQL
            db_user = os.getenv("MYSQLUSER", "root")
            db_password = os.getenv("MYSQLPASSWORD", "Password%401234%23")
            db_host = os.getenv("MYSQLHOST", "localhost")
            db_name = os.getenv("MYSQLDB", "bookstore")

            app.config["SQLALCHEMY_DATABASE_URI"] = (
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}"
            )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

    # =========================
    # INIT EXTENSIONS
    # =========================
    db.init_app(app)
    from models import User,Payment,OrderItem,Address,Category,Book,Order,CartItem
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    bcrypt = Bcrypt(app)

    # =========================
    # LOGIN MANAGER
    # =========================
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        flash("You must login first.", "error")
        return redirect(url_for("login"))

    # =========================
    # ROUTES
    # =========================
    from route import register_routes
    register_routes(app, db, bcrypt)

    return app
