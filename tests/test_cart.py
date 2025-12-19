# tests/test_cart.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import CartItem

def test_cart_empty_redirects_to_books_page(logged_in_client):
    r = logged_in_client.get("/cart", follow_redirects=False)
    assert r.status_code == 302  # empty -> redirect to /bookspage

def test_add_to_cart_creates_item(logged_in_client, sample_book):
    r = logged_in_client.post(f"/cart/{sample_book.id}", data={"quantity": "2"}, follow_redirects=True)
    assert r.status_code == 200
    item = CartItem.query.filter_by(book_id=sample_book.id).first()
    assert item is not None and item.quantity == 2

def test_update_cart_changes_quantity(logged_in_client, sample_book):
    logged_in_client.post(f"/cart/{sample_book.id}", data={"quantity": "1"}, follow_redirects=True)
    r = logged_in_client.post(f"/update_cart/{sample_book.id}", data={"quantity": "5"}, follow_redirects=True)
    assert r.status_code == 200
    item = CartItem.query.filter_by(book_id=sample_book.id).first()
    assert item.quantity == 5

def test_remove_from_cart_deletes_item_and_redirects(logged_in_client, sample_book):
    logged_in_client.post(f"/cart/{sample_book.id}", data={"quantity": "1"}, follow_redirects=True)
    r = logged_in_client.get(f"/remove_from_cart/{sample_book.id}", follow_redirects=False)
    assert r.status_code in (302, 200)  # route redirects after removal
    item = CartItem.query.filter_by(book_id=sample_book.id).first()
    assert item is None
