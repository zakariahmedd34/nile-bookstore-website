from collections import defaultdict
from flask import flash, redirect, render_template, request, url_for
from models import CartItem, Category, User ,Book
from seed_db import seed_real_books, seed_categories
from flask_login import login_user, logout_user, login_required, current_user


def register_routes(app,db,bcrypt):
    @app.route('/') 
    def home():
        books = Book.query.all()
        categories = Category.query.all()

        cat_list = {}
        for cat in categories:
            cat_list[cat.id] = [b for b in books if  b.category_id == cat.id]
        
        return render_template('home.html', css_file='home.css', cat_list=cat_list, categories=categories
                               ,id = current_user.get_id() if current_user.is_authenticated else None,
                                is_admin = current_user.is_admin if current_user.is_authenticated else False
                               ,fname = current_user.fname if current_user.is_authenticated else None) 
    
    #!-----------------------------------------------------------Authentication -------------------------------------------------
    @app.route("/register", methods=['GET', 'POST'])
    def register():

        if request.method == 'GET':
            return render_template('register.html', css_file='register.css')

        # POST
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #  Check empty fields
        if not all([fname, lname, username, email,password, confirm_password]):
            return render_template("register.html", css_file='register.css', error="All fields are required.")

        #  Check password match
        if password != confirm_password:
            return render_template("register.html", css_file='register.css', error="Passwords do not match.")

        #  Check if email already exists
        if User.query.filter_by(email=email).first():
            return render_template("register.html", css_file='register.css', error="Email is already registered.")
        #  Check if username already exists
        if User.query.filter_by(user_name=username).first():
            return render_template("register.html", css_file='register.css', error="Username is already taken.")

        #  Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        #  Create user
        new_user = User(
            fname=fname,
            lname=lname,
            user_name=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html', css_file='login.css')

        # POST
        username = request.form.get('username')
        password = request.form.get('password')

        # Check empty fields
        if not username or not password:
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Both username and password are required."
            )

        # Find user by username
        user = User.query.filter_by(user_name=username).first()

        if not user:
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Invalid username or password."
            )

        # Check password
        if not bcrypt.check_password_hash(user.password, password):
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Invalid username or password."
            )

        # Login success
        login_user(user)
        return redirect(url_for('home'))
        
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for('home'))

    #?--------------------------------Admin Routes-------------------------------------------------------------
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        return f"Hollo {current_user.fname} This is the admin dashboard."
    @app.route('/bookdetails/<int:book_id>-<slug>')

    #!--------------------------------------------Book Routes--------------------------------------------------------
    def book_details(book_id, slug):
        book = Book.query.get_or_404(book_id)
        return render_template('bookdetails.html', css_file='bookdetails.css', book=book)

    @app.route('/bookspage')
    def books_page():
        return render_template('bookpage.html', css_file='BooksPage.css', books=Book.query.all())
    @app.route('/categories')
    def categories():
        categories = Category.query.all()
        return render_template('categories.html', css_file='categories.css', categories=categories)
    @app.route('/categories/<int:cat_id>-<slug>')
    def view_category_books(cat_id, slug):
        category = Category.query.get_or_404(cat_id)
        books = Book.query.filter_by(category_id=cat_id).all()
        return render_template('bookpage.html', category=category, books=books,css_file='BooksPage.css')\
    #------------------------------------------------------------------------------------------------------
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html', css_file='profile.css')
#!-------------------------------------  Cart -------------------------------------------------------------------------------------
    @app.route('/cart')
    @login_required
    def cart():
        def cartItems():
            items = CartItem.query.filter_by(user_id = current_user.id).all()
            list_books = defaultdict(list)
            for item in items:
                book = Book.query.filter_by(id = item.book_id).first()
                list_books[item.quantity].append(book)
            return list_books
        

        if CartItem.query.filter_by(user_id=current_user.id).first():
            return render_template('cart.html', css_file='cart.css',cart_items = cartItems())
        
        flash("Your cart is empty!", "info")
        return redirect(url_for('books_page'))
    
    @app.route('/cart/<int:book_id>', methods=['POST','GET'])
    @login_required
    def add_to_cart(book_id):  
                
        quantity_str = request.form.get('quantity')
        existing_item = CartItem.query.filter_by(user_id = current_user.id, book_id = book_id).first()
        try:
            quantity = int(quantity_str)
            if existing_item is None:
                new_cart_item = CartItem(
                    user_id = current_user.id,
                    book_id = book_id,
                    quantity = quantity
                )
                db.session.add(new_cart_item)
                flash("Book added to cart!", "success")
            else:
                existing_item.quantity += quantity
                flash("Book quantity updated in cart!", "success")
                
            db.session.commit()
            return redirect(url_for('cart'))

        except Exception as e:
            flash("Something went wrong.", "error")
            return redirect(url_for('cart'))
        
    @app.route('/update_cart/<int:book_id>', methods=['POST'])
    @login_required
    def update_cart(book_id):
        quantity_str = request.form.get('quantity', '0')
        try:
            q = int(quantity_str)
            exsisting_item = CartItem.query.filter_by(user_id = current_user.id, book_id = book_id).first()
            exsisting_item.quantity = q
            db.session.commit()
            flash("Cart updated successfully.", "success")
            return redirect(url_for('cart'))
        except Exception as e:
            flash("Invalid quantity.", "error")
            return str(e)
        
    @app.route('/remove_from_cart/<int:book_id>')
    @login_required
    def remove_from_cart(book_id):  
        r_item = CartItem.query.filter_by(book_id = book_id , user_id = current_user.id).first_or_404()
        try:
            db.session.delete(r_item)
            db.session.commit()	
            flash("Item removed from cart.", "success")
            if not CartItem.query.filter_by(user_id=current_user.id).first():
                flash("Your cart is empty!", "info")
                return redirect(url_for('books_page'))
    
            return redirect(url_for('cart'))
        except Exception as e:
            return str(e)
        
#!--------------------------------------------------------------------------------------------------------------------------------------------------------------
#!--------------------------------------------------------------------------------------------------------------------------------------------------------------
#!checkout--------------------------------------------------------------------------------
    @app.route('/checkout')
    def checkout():
        return render_template('checkout.html', css_file='checkout.css')

    @app.route('/seed_db')
    def seed():
        seed_categories()
        seed_real_books()
        return "Database seeded with real books!"
    

