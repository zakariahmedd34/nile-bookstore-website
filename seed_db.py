from app import db
from models import Book, Category
from datetime import datetime

def seed_books():
    try:
        print("Starting database seeding...")
        
        category = Category.query.filter_by(name="Novel").first()
        if not category:
            category = Category(name="Novel")
            db.session.add(category)
            db.session.commit()
            print(f"Created category: Novel (ID: {category.id})")
        
        Book.query.delete()
        db.session.commit()
        print("Cleared existing books")
        
        books = [
            Book(
                title="Pride and Prejudice",
                author="Jane Austen",
                description="A romantic novel that explores manners, upbringing, and society in early 19th-century England.",
                publisher="Penguin Classics",
                publication_date=datetime(1813, 1, 28).date(),
                price=100,
                cover_url="https://covers.openlibrary.org/b/id/8091013-L.jpg",
                pdf_url=None,
                category_id=category.id
            ),
            Book(
                title="1984",
                author="George Orwell",
                description="A dystopian novel about a totalitarian regime that uses surveillance and mind control.",
                publisher="Secker & Warburg",
                publication_date=datetime(1949, 6, 8).date(),
                price=120,
                cover_url="https://covers.openlibrary.org/b/id/7222246-L.jpg",
                pdf_url=None,
                category_id=category.id
            ),
            Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                description="A novel set in the Jazz Age that explores themes of wealth, love, and the American Dream.",
                publisher="Charles Scribner's Sons",
                publication_date=datetime(1925, 4, 10).date(),
                price=110,
                cover_url="https://covers.openlibrary.org/b/id/11153255-L.jpg",
                pdf_url=None,
                category_id=category.id
            ),
            Book(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                description="A story of racial injustice and childhood innocence in the American South.",
                publisher="J.B. Lippincott & Co.",
                publication_date=datetime(1960, 7, 11).date(),
                price=130,
                cover_url="https://covers.openlibrary.org/b/id/8228691-L.jpg",
                pdf_url=None,
                category_id=category.id
            ),
            Book(
                title="The Catcher in the Rye",
                author="J.D. Salinger",
                description="A novel about teenage rebellion, identity, and the struggles of growing up.",
                publisher="Little, Brown and Company",
                publication_date=datetime(1951, 7, 16).date(),
                price=115,
                cover_url="https://covers.openlibrary.org/b/id/8231856-L.jpg",
                pdf_url=None,
                category_id=category.id
            )
        ]
        
        db.session.add_all(books)
        db.session.commit()
        
        print(f"✅ Successfully added {len(books)} books to database")
        
        # Verify
        for book in Book.query.all():
            print(f"  - {book.title}")
        
        return f"Successfully seeded {len(books)} books!"
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return f"Error seeding database: {str(e)}"