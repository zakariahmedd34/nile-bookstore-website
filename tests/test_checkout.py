# tests/test_checkout.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock

def login_and_add_book(logged_in_client, sample_book):
    # Add book to cart
    r = logged_in_client.post(f"/cart/{sample_book.id}", data={"quantity": "2"}, follow_redirects=True)
    assert r.status_code == 200

def ensure_saved_address(app):
    # Create a saved address for the current user (id=1 under test fixtures)
    with app.app_context():
        from models import Address, db
        a = Address(user_id=1, user_fname="Saved", user_lname="Addr",
                    city="Giza", country="Egypt", street_line1="Line 1",
                    postal_code="12511", phone_number="01000000000")
        db.session.add(a); db.session.commit()
        return a.id

def test_checkout_cash_with_saved_address(app, logged_in_client, sample_book):
    login_and_add_book(logged_in_client, sample_book)
    address_id = ensure_saved_address(app)

    data = {
        "payment_method": "Cash",
        "address_id": str(address_id)  # use saved address
    }
    r = logged_in_client.post("/checkout", data=data, follow_redirects=False)
    # Should redirect to confirmation page
    assert r.status_code == 302
    assert "/order-confirmed/" in r.headers.get("Location", "")

    # Confirm order exists, cart cleared
    with app.app_context():
        from models import Order, OrderItem, CartItem
        orders = Order.query.filter_by(user_id=1).all()
        assert len(orders) >= 1
        oi = OrderItem.query.filter_by(order_id=orders[-1].id).all()
        assert len(oi) == 1 and oi[0].quantity == 2
        assert CartItem.query.filter_by(user_id=1).count() == 0

def test_checkout_cash_with_new_address(logged_in_client, sample_book):
    login_and_add_book(logged_in_client, sample_book)

    data = {
        "payment_method": "Cash",
        # No address_id → create new
        "user_fname": "New",
        "user_lname": "Address",
        "city": "Giza",
        "country": "Egypt",
        "street_line1": "New St 1",
        "street_line2": "",
        "street_line3": "",
        "state": "Giza",
        "postal_code": "12511",
        "phone_number": "01000000000"
    }
    r = logged_in_client.post("/checkout", data=data, follow_redirects=False)
    assert r.status_code == 302
    
    assert "/order-confirmed/" in r.headers.get("Location", "")

def test_checkout_card_with_saved_address_success(app, logged_in_client, sample_book, monkeypatch):
    login_and_add_book(logged_in_client, sample_book)
    address_id = ensure_saved_address(app)

    # Mock Stripe Session.create
    fake_session = MagicMock()
    fake_session.id = "cs_test_123"
    fake_session.url = "https://stripe.example/checkout/session/cs_test_123"
    fake_session.payment_intent = "pi_test_123"
    monkeypatch.setattr("route.stripe.checkout.Session.create", lambda **kwargs: fake_session)

    # Post checkout with Visa
    data = {
        "payment_method": "Visa",
        "address_id": str(address_id)
    }
    r = logged_in_client.post("/checkout", data=data, follow_redirects=False)
    # Should redirect to Stripe (mock URL)
    assert r.status_code == 302

    assert r.headers.get("Location") == fake_session.url

    # Now simulate Stripe success callback
    # Mock Session.retrieve to show payment_status=paid and matching order id
    def mock_retrieve(session_id):
        m = MagicMock()
        m.payment_status = "paid"
        # The order_id is embedded in success_url / metadata; we don't know it here,
        # so we call success route with the one created in DB:
        from models import Order
        with app.app_context():
            latest_order = Order.query.filter_by(user_id=1).order_by(Order.id.desc()).first()
            m.client_reference_id = str(latest_order.id)
        m.id = "cs_test_123"
        m.payment_intent = "pi_test_123"
        return m

    monkeypatch.setattr("route.stripe.checkout.Session.retrieve", mock_retrieve)

    # Find latest order and hit success route
    with app.app_context():
        from models import Order
        order = Order.query.filter_by(user_id=1).order_by(Order.id.desc()).first()
        assert order is not None
        success_url = f"/pay/success/{order.id}?session_id=cs_test_123"

    r2 = logged_in_client.get(success_url, follow_redirects=True)
    assert r2.status_code == 200

    # Verify payment success and cart cleared
    with app.app_context():
        from models import Payment, CartItem
        p = Payment.query.filter_by(order_id=order.id).order_by(Payment.id.desc()).first()
        assert p and p.status == "Success"
        assert CartItem.query.filter_by(user_id=1).count() == 0

def test_checkout_card_cancel_flow(app, logged_in_client, sample_book, monkeypatch):
    login_and_add_book(logged_in_client, sample_book)
    address_id = ensure_saved_address(app)

    # Mock create as before
    fake_session = MagicMock()
    fake_session.id = "cs_test_cancel"
    fake_session.url = "https://stripe.example/checkout/session/cs_test_cancel"
    fake_session.payment_intent = "pi_test_cancel"
    monkeypatch.setattr("route.stripe.checkout.Session.create", lambda **kwargs: fake_session)

    r = logged_in_client.post("/checkout",
                              data={"payment_method": "Visa", "address_id": str(address_id)},
                              follow_redirects=False)
    assert r.status_code == 302

    # Simulate cancel route
    with app.app_context():
        from models import Order
        order = Order.query.filter_by(user_id=1).order_by(Order.id.desc()).first()

    r2 = logged_in_client.get(f"/pay/cancel/{order.id}", follow_redirects=True)
    assert r2.status_code == 200
    assert b"Payment canceled" in r2.data
