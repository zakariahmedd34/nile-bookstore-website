import requests
from app import db
from models import Book, Category
from datetime import datetime
import random

SEARCH_TERMS = [
    "science", "fantasy", "history", "business", "romance",
    "technology", "children", "biography", "mystery", "art"
]

def seed_categories():
    categories = {}
    for name in [
        "Science", "Fantasy", "History", "Business", "Romance",
        "Technology", "Children", "Biography", "Mystery", "Art"
    ]:
        cat = Category(name=name)
        db.session.add(cat)
        categories[name] = cat
    db.session.commit()
    return categories


def seed_real_books(limit=100):
    print("Fetching books from Google Books API...")

    categories = seed_categories()

    total_added = 0

    for term in SEARCH_TERMS:
        if total_added >= limit:
            break

        url = f"https://www.googleapis.com/books/v1/volumes?q={term}&maxResults=40"
        response = requests.get(url).json()

        if "items" not in response:
            continue

        for item in response["items"]:
            if total_added >= limit:
                break

            info = item.get("volumeInfo", {})

            title = info.get("title")
            authors = info.get("authors")
            description = info.get("description")
            publisher = info.get("publisher")
            published = info.get("publishedDate")
            categories_list = info.get("categories", ["General"])
            image = info.get("imageLinks", {}).get("thumbnail")

            if len(title) > 25:
                continue  # skip this book (bad data)

            if not title or not image or not authors or not publisher or not published or not description:
                continue  # لازم يكون فيه عنوان وصورة غلاف

            # تحويل تاريخ النشر
            try:
                published_date = datetime.strptime(published[:10], "%Y-%m-%d")
            except:
                published_date = datetime(2000, 1, 1)

            # تحديد الفئة
            category_name = categories_list[0].split("/")[0]
            category_obj = categories.get(category_name, list(categories.values())[0])

            # عمل Book object
            book = Book(
                title=title,
                author=authors[0],
                description=description,
                publisher=publisher,
                publication_date=published_date,
                price=random.randint(50, 500),
                pdf_url="https://example.com/book.pdf",
                cover_url=image,
                category_id=category_obj.id
            )

            db.session.add(book)
            total_added += 1

    db.session.commit()
    return f"Added {total_added} real books successfully!"
