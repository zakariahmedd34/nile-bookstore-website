from app import create_app, db
from models import Book, Category

app = create_app()

with app.app_context():
    print("=" * 50)
    print("SEEDING DATABASE")
    print("=" * 50)
    
    # First, make sure tables exist
    print("Creating tables if they don't exist...")
    db.create_all()
    
    # Check current state
    book_count = Book.query.count()
    category_count = Category.query.count()
    
    print(f"Current state: {book_count} books, {category_count} categories")
    
    if book_count == 0:
        print("\nDatabase is empty. Seeding now...")
        
        # Add categories
        categories = ["Novel", "Science Fiction", "Mystery", "Biography", "Textbook"]
        for cat_name in categories:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
                print(f"  Added category: {cat_name}")
        
        db.session.commit()
        
        # Add sample books
        books_data = [
            {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "description": "A romantic novel that explores manners, upbringing, and society.",
                "publisher": "Penguin Classics",
                "price": 100,
                "cover_url": "https://covers.openlibrary.org/b/id/8091013-L.jpg",
                "category_id": 1
            },
            {
                "title": "1984",
                "author": "George Orwell", 
                "description": "A dystopian novel about totalitarian regime.",
                "publisher": "Secker & Warburg",
                "price": 120,
                "cover_url": "https://covers.openlibrary.org/b/id/7222246-L.jpg",
                "category_id": 1
            },
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "description": "A novel set in the Jazz Age.",
                "publisher": "Charles Scribner's Sons",
                "price": 110,
                "cover_url": "https://covers.openlibrary.org/b/id/11153255-L.jpg",
                "category_id": 1
            }
        ]
        
        for book_data in books_data:
            book = Book(**book_data)
            db.session.add(book)
            print(f"  Added book: {book_data['title']}")
        
        db.session.commit()
        
        # Verify
        final_book_count = Book.query.count()
        final_category_count = Category.query.count()
        
        print(f"\nSeeding complete!")
        print(f"Now have: {final_book_count} books, {final_category_count} categories")
        
    else:
        print(f"\nDatabase already has {book_count} books")
        print("Books in database:")
        for book in Book.query.all():
            print(f"  - {book.title} by {book.author}")
    
    print("\n" + "=" * 50)