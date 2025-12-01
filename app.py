from flask import Flask   
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    
    app = Flask(__name__, template_folder='templates', static_folder='static')
    sql_server_password = " "
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:{sql_server_password}@localhost:3306/bookstore"

    db.init_app(app)

    from route import register_routes
    register_routes(app,db)

    migrate = Migrate(app,db)

    return app

    