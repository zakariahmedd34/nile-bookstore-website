from flask import render_template, request
from models import User  


def register_routes(app,db):
    @app.route('/') 
    def home():
        return render_template('home.html', css_file='home.css')
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





# @app.route('/') 
# def home():
#     return render_template('home.html', css_file='home.css')


