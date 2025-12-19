# tests/test_auth.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_register_success_then_login(client):
    reg = {
        "fname": "A", "lname": "B",
        "username": "newuser",
        "email": "new@example.com",
        "password": "Pass123!", "confirm_password": "Pass123!"
    }
    r = client.post("/register", data=reg, follow_redirects=True)
    assert r.status_code == 200  # landed on login page

    r2 = client.post("/login",
                     data={"username": "newuser", "password": "Pass123!"},
                     follow_redirects=True)
    assert r2.status_code == 200
    assert b"Login" in r2.data or b"Home" in r2.data  # template content sanity

def test_register_missing_fields_shows_error(client):
    reg = {
        "fname": "A", "lname": "B",
        "username": "",  # missing username
        "email": "no_user@example.com",
        "password": "Pass123!", "confirm_password": "Pass123!"
    }
    r = client.post("/register", data=reg)
    assert r.status_code == 200
    assert b"All fields are required." in r.data

def test_login_invalid_password(client, register_user):
    r = client.post("/login",
                    data={"username": register_user["username"], "password": "WrongPass"},
                    follow_redirects=False)
    assert r.status_code == 200
    assert b"Invalid username or password." in r.data

def test_logout_then_protected_redirect(logged_in_client):
    r = logged_in_client.get("/logout", follow_redirects=True)
    assert r.status_code == 200
    assert b"You have been logged out." in r.data
    r2 = logged_in_client.get("/cart", follow_redirects=False)
    # LoginManager unauthorized handler redirects to /login
    assert r2.status_code == 302
