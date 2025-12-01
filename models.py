from app import db
from datetime import datetime
from sqlalchemy import Enum



class User(db.Model):
    __tablename__="user"

    id = db.Column(db.Integer, primary_key = True)

    fname = db.Column(db.String(30),nullable= False)
    lname = db.Column(db.String(30),nullable= False)
    user_name = db.Column(db.String(30),nullable= False)
    phone = db.Column(db.String(25),nullable= False)
    email = db.Column(db.String(125),unique = True,nullable= False)
    password = db.Column(db.String(70),nullable = False)
    is_admin = db.Column(db.Boolean, default=False)


    #! Relationships
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    reviews = db.relationship("Rate",backref='user',lazy=True)
    orders = db.relationship("Order",backref='user',lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __repr__(self):
        return f"User {self.fname}, {self.lname}, {self.user_name}"

#?----------------------------------------------------------------------------------------
class Category(db.Model):
    __tablename__="category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable = False)

    books = db.relationship('Book', backref='category', lazy=True)
#?----------------------------------------------------------------------------------------
class Book(db.Model):
    __tablename__= "book"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    publisher = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    price = db.Column(db.Integer, default=0)
    pdf_url = db.Column(db.String(255), nullable=True)
    cover_url = db.Column(db.String(255), nullable=True)

    #!FK
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    #!Relationships
    cart_items = db.relationship('CartItem', backref='book', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='book', lazy=True)
    reviews = db.relationship('Rate', backref='book', lazy=True)
    order_items = db.relationship('OrderItem', backref='book', lazy=True)

    def __repr__(self):
        return f"Book {self.title}"

#?----------------------------------------------------------------------------------------
class Rate(db.Model):
    __tablename__="rate"

    rate_value = db.Column(db.Float) # (1-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #!FK,PK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    def __repr__(self):
        return f"Rate user={self.user_id} book={self.book_id}"
class CartItem(db.Model):
    __tablename__ = "cart_item"
    quantity = db.Column(db.Integer,default = 1)

    #!FK,PK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)

    def __repr__(self):
        return f"CartItem user={self.user_id} book={self.book_id}"
#?----------------------------------------------------------------------------------------
class Wishlist(db.Model):
    __tablename__ = "wishlist"

    #!FK,PK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)

    def __repr__(self):
        return f"Wishlist user={self.user_id} book={self.book_id}"
#?----------------------------------------------------------------------------------------
class Address(db.Model):
    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key = True)

    user_fname = db.Column(db.String(30),nullable= False)
    user_lname = db.Column(db.String(30),nullable= False)
    city = db.Column(db.String(30),nullable= False)
    country = db.Column(db.String(40),nullable = False)
    street_line1 = db.Column(db.String(255), nullable=False)
    street_line2 = db.Column(db.String(255),default=None)
    street_line3 = db.Column(db.String(255),default=None)
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(25), nullable=False)
    
    #!FK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #!Relationships
    orders = db.relationship('Order', backref='shipping_address', lazy=True)

    def __repr__(self):
        return f"Address {self.id}"
#?----------------------------------------------------------------------------------------
class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)

    order_status = db.Column(
    Enum(
        "Pending",
        "Shipped",
        "Delivered",
        name="order_status"
    ),
    default="Pending",
    nullable=False
    )   

    total_amount = db.Column(db.Float, nullable=False, default=0)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    payment_method = db.Column(
        Enum("Cash", "Visa", "Mastercard", name="order_payment_method"),
        nullable=False,
        default="Cash"
    )

    # !FK
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    #!Relationship
    items = db.relationship('OrderItem', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)

    def __repr__(self):
        return f"Order {self.id}"
#?----------------------------------------------------------------------------------------
class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer,default = 1)
    unit_price = db.Column(db.Float, nullable=False)
    
    #!Relationship
    book_id =  db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    order_id =  db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    def __repr__(self):
        return f"OrderItem {self.id}"
 #?----------------------------------------------------------------------------------------
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)

    amount_paid = db.Column(db.Float, nullable=False)

    status = db.Column(
        Enum("Pending", "Success", "Failed", name="payment_status"),
        default="Pending",
        nullable=False
    )

    payment_method = db.Column(
        Enum("Visa", "Mastercard", "Wallet", "Fawry", "ValU", name="payment_method"),
        nullable=False
    )

    transaction_id = db.Column(db.String(100))     
    payment_reference = db.Column(db.String(100))   
    failure_reason = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    #! FK
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Payment {self.id}"
