from app import create_app
from seed_db import seed_real_books
from models import Category, Book

app = create_app()
with app.app_context():
    print(seed_real_books(limit=50))
    print("Final:", "categories=", Category.query.count(), "books=", Book.query.count())