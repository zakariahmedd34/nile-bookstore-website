from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # =========================
    # CONFIG (SQLite فقط)
    # =========================
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "dev-secret-key"

    # =========================
    # INIT EXTENSIONS
    # =========================
    db.init_app(app)

    from models import User, Payment, OrderItem, Address, Category, Book, Order, CartItem

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    bcrypt = Bcrypt(app)

    # =========================
    # LOGIN MANAGER
    # =========================
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
