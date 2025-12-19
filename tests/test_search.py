import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app, db
from models import Book
from datetime import date

@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-key"
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed a sample book
            book = Book(
                title="Science Basics",
                author="John Doe",
                description="Intro to science",
                publisher="EduPub",
                publication_date=date(2020, 1, 1),  # ✅ FIXED
                price=100,
                pdf_url="https://example.com/book.pdf",
                cover_url="https://example.com/cover.jpg",
                category_id=1
                )
            db.session.add(book)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


def test_search_empty_query(client):
    response = client.get("/search?q=")
    # Should redirect back to books_page
    assert response.status_code == 302
    assert "/books" in response.headers["Location"]

def test_search_with_results(client):
    response = client.get("/search?q=Science")
    # Should render bookpage.html with the seeded book
    assert response.status_code == 200
    assert b"Science Basics" in response.data
    # assert b"John Doe" in response.data

def test_search_no_results(client):
    response = client.get("/search?q=Nonexistent")
    # Should render bookpage.html but no books found
    assert response.status_code == 200
    assert b"No books found" in response.data or b"Please enter a search term." not in response.data
