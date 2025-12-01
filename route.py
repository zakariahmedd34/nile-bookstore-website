from flask import render_template, request
from models import User ,Book
from seed_db import seed_books

def register_routes(app,db):
    @app.route('/') 
    def home():
        books = Book.query.all()
        return render_template('home.html', css_file='home.css', books=books)
    
    @app.route('/second_homepage')
    def home_page():
        books = Book.query.all()
        return render_template('homepage2.html',css_file ='home.css',books = books) 

    @app.route('/bookdetail')
    def book_details():
        return render_template('bookdetails.html', css_file='bookdetails.css')

    @app.route('/bookspage')
    def books_page():
        return render_template('bookpage.html', css_file='BooksPage.css')

    @app.route('/categories')
    def categories():
        return render_template('categories.html', css_file='categories.css')

    @app.route('/cart')
    def cart():
        return render_template('cart.html', css_file='cart.css')

    @app.route('/checkout')
    def checkout():
        return render_template('checkout.html', css_file='checkout.css')

    @app.route('/contact')
    def contact():
        return render_template('contact.html', css_file='contact.css')

    @app.route('/login', methods=['GET'])
    def login():
        return render_template('login.html', css_file='login.css')
    @app.route('/register')
    def register():
        return render_template('register.html', css_file='register.css')

    @app.route('/profile')
    def profile():
        return render_template('profile.html', css_file='profile.css')

    @app.route('/show_users')
    def index():
        users = User.query.all()
        return render_template("test.html",people = str(users))
    @app.route('/seed_db')
    def seed():
        return render_template("test.html",people =  seed_books())
    
    @app.route('/debug_books')
    def debug_books():
        from app import db
        from models import Book, Category
        
        # Check counts
        book_count = Book.query.count()
        category_count = Category.query.count()
        
        # Get all books
        books = Book.query.all()
        
        # Prepare debug info
        debug_info = f"""
        <h2>Database Debug Info</h2>
        <p>📚 Books in database: {book_count}</p>
        <p>🏷️ Categories in database: {category_count}</p>
        <hr>
        """
        
        if books:
            debug_info += "<h3>Books List:</h3><ul>"
            for book in books:
                debug_info += f"""
                <li>
                    <strong>{book.title}</strong> by {book.author}<br>
                    Price: {book.price} EGP<br>
                    Cover URL: {book.cover_url}<br>
                    Category ID: {book.category_id}
                </li>
                <hr>
                """
            debug_info += "</ul>"
        else:
            debug_info += "<p style='color: red;'>❌ No books found in database!</p>"
        
        return debug_info




# @app.route('/') 
# def home():
#     return render_template('home.html', css_file='home.css')


