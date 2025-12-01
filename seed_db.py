from app import db
from models import Book,Category

def seed_books():
    category = Category(name="Novel")
    db.session.add(category)
    db.session.commit()
    books = [
        Book(
            title="Pride and Prejudice",
            author="Jane Austen",
            description="A romantic novel that explores manners, upbringing, and society in early 19th-century England.",
            publication_date=None,
            price=100,
            cover_url="https://covers.openlibrary.org/b/id/8091013-L.jpg",
            pdf_url=None,
            category_id=1
        ),
        Book(
            title="1984",
            author="George Orwell",
            description="A dystopian novel about a totalitarian regime that uses surveillance and mind control.",
            publication_date=None,
            price=120,
            cover_url="https://covers.openlibrary.org/b/id/7222246-L.jpg",
            pdf_url=None,
            category_id=1
        ),
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            description="A novel set in the Jazz Age that explores themes of wealth, love, and the American Dream.",
            publication_date=None,
            price=110,
            cover_url="https://covers.openlibrary.org/b/id/11153255-L.jpg",
            pdf_url=None,
            category_id=1
        ),
        Book(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            description="A story of racial injustice and childhood innocence in the American South.",
            publication_date=None,
            price=130,
            cover_url="https://covers.openlibrary.org/b/id/8228691-L.jpg",
            pdf_url=None,
            category_id=1
        ),
        Book(
            title="The Catcher in the Rye",
            author="J.D. Salinger",
            description="A novel about teenage rebellion, identity, and the struggles of growing up.",
            publication_date=None,
            price=115,
            cover_url="https://covers.openlibrary.org/b/id/8231856-L.jpg",
            pdf_url=None,
            category_id=1
        ),
    ]
    db.session.add_all(books)
    db.session.commit()
    return "Books seeded!"