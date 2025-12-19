# tests/conftest.py
import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app, db
from models import User, Book, Category

@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    }
    app = create_app(test_config)

    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# --- Auth helpers ---
@pytest.fixture
def register_user(client):
    data = {
        "fname": "Test",
        "lname": "User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "Secret123!",
        "confirm_password": "Secret123!",
    }
    client.post("/register", data=data, follow_redirects=True)
    return data

@pytest.fixture
def logged_in_client(client, register_user):
    client.post("/login",
                data={"username": register_user["username"], "password": register_user["password"]},
                follow_redirects=True)
    return client

# --- Data helpers for cart ---
@pytest.fixture
def sample_category(app):
    cat = Category(name="Testing")
    db.session.add(cat); db.session.commit()
    return cat

@pytest.fixture
def sample_book(app, sample_category):
    b = Book(
        title="Test Book",
        author="Tester",
        price=100,
        category_id=sample_category.id
    )
    db.session.add(b); db.session.commit()
    return b
