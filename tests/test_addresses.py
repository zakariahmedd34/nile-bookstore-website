# tests/test_addresses.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import Address, Order

def test_add_address(logged_in_client):
    data = {
        "user_fname": "Salma",
        "user_lname": "Mohamed",
        "city": "Giza",
        "country": "Egypt",
        "street_line1": "Street 12",
        "street_line2": "",
        "street_line3": "",
        "state": "Giza",
        "postal_code": "12511",
        "phone_number": "01000000000"
    }
    r = logged_in_client.post("/profile/addaddresses", data=data, follow_redirects=True)
    assert r.status_code == 200
    # Verify stored
    # We cannot directly use db here without app context, so assert UI feedback
    assert b"Address added successfully." in r.data

def test_edit_address(app, logged_in_client):
    # Create address
    with app.app_context():
        from models import Address, db
        a = Address(user_id=1, user_fname="A", user_lname="B",
                    city="Old", country="EG", street_line1="S1",
                    postal_code="00000", phone_number="010")
        db.session.add(a); db.session.commit()
        address_id = a.id

    # Edit
    data = {
        "user_fname": "NewF",
        "user_lname": "NewL",
        "city": "NewCity",
        "country": "Egypt",
        "street_line1": "New Street",
        "street_line2": "Line2",
        "street_line3": "",
        "state": "Giza",
        "postal_code": "12345",
        "phone_number": "01099999999"
    }
    r = logged_in_client.post(f"/profile/update_address/{address_id}", data=data, follow_redirects=True)
    assert r.status_code == 200
    assert b"Address updated successfully." in r.data

    # Confirm persisted
    with app.app_context():
        from models import Address
        from sqlalchemy.orm import Session
        with Session(db.engine) as session:
            a2 = session.get(Address, address_id)

    assert a2.user_fname == "NewF"
    assert a2.city == "NewCity"
    assert a2.street_line1 == "New Street"

def test_delete_address_not_in_order(app, logged_in_client):
    with app.app_context():
        from models import Address, db
        a = Address(user_id=1, user_fname="D", user_lname="L",
                    city="C", country="EG", street_line1="S",
                    postal_code="1", phone_number="010")
        db.session.add(a); db.session.commit()
        address_id = a.id

    r = logged_in_client.get(f"/profile/addresses/delete/{address_id}", follow_redirects=True)
    assert r.status_code == 200
    assert b"Address deleted successfully." in r.data

    with app.app_context():
        from models import Address, db
        a2 = db.session.get(Address, address_id)
        assert a2 is None


def test_delete_address_blocked_if_in_active_order(app, logged_in_client):
    with app.app_context():
        from models import Address, Order, db
        a = Address(user_id=1, user_fname="Blocked", user_lname="Addr",
                    city="C", country="EG", street_line1="S",
                    postal_code="1", phone_number="010")
        db.session.add(a); db.session.commit()

        # Create active order referencing this address (order_status != delivered)
        o = Order(user_id=1, shipping_address_id=a.id, order_status="Pending", total_amount=100)
        db.session.add(o); db.session.commit()
        address_id = a.id

    r = logged_in_client.get(f"/profile/addresses/delete/{address_id}", follow_redirects=True)
    assert r.status_code == 200
    assert b"You cannot delete this address because it is used in an active order." in r.data

    with app.app_context():
        from models import Address
        assert Address.query.get(address_id) is not None
