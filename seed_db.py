import requests
from app import db
from models import Book, Category
from datetime import datetime
import random

# =========================
# CONFIG
# =========================

SEARCH_TERMS = [
    "science", "fantasy", "history", "business", "romance",
    "technology", "children", "biography", "mystery", "art"
]

CATEGORY_IMAGES = {
    "Science": "https://images.unsplash.com/photo-1532094349884-543bc11b234d",
    "Fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "History": "https://images.unsplash.com/photo-1461360370896-922624d12aa1",
    "Business": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",
    "Romance": "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "Technology": "https://images.unsplash.com/photo-1518770660439-4636190af475",
    "Children": "https://images.unsplash.com/photo-1607082349566-187342175e2f",
    "Biography": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e",
    "Mystery": "https://images.unsplash.com/photo-1505506874110-6a7a69069a08",
    "Art": "https://images.unsplash.com/photo-1496317899792-9d7dbcd928a1",
}

def seed_categories():
    categories = {}

    for name, image in CATEGORY_IMAGES.items():
        category = Category.query.filter_by(name=name).first()
        if not category:
            category = Category(name=name, cover_url=image)
            db.session.add(category)
        categories[name] = category

    db.session.commit()
    print(" Categories seeded")
    return categories


def seed_books(limit=200):
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
            categories_list = info.get("categories", [])
            image = info.get("imageLinks", {}).get("thumbnail")

            if not all([title, authors, description, publisher, published, image]):
                continue
            if len(title) > 80:
                continue
            if Book.query.filter_by(title=title).first():
                continue

            try:
                published_date = datetime.strptime(published[:10], "%Y-%m-%d")
            except:
                published_date = datetime(2000, 1, 1)

            category_name = categories_list[0].split("/")[0] if categories_list else "Science"
            category = categories.get(category_name, list(categories.values())[0])

            book = Book(
                title=title,
                author=authors[0],
                description=description[:500],
                publisher=publisher,
                publication_date=published_date,
                price=random.randint(80, 600),
                pdf_url="https://example.com/book.pdf",
                cover_url=image,
                category_id=category.id
            )

            db.session.add(book)
            total_added += 1

    db.session.commit()
    print(f" Added {total_added} books successfully")
