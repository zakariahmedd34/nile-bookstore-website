from collections import defaultdict
from flask import flash, redirect, render_template, request, url_for
from models import CartItem, Category, User ,Book, Address, Order, OrderItem, Payment
from seed_db import seed_real_books, seed_categories
from flask_login import login_user, logout_user, login_required, current_user
import stripe
import os
from dotenv import load_dotenv
load_dotenv()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "").strip()

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
    def _get_cart_lines(user_id: int):
        items = CartItem.query.filter_by(user_id=user_id).all()
        lines = []
        total = 0

        for cartitem in items:
            book = Book.query.get(cartitem.book_id)
            if not book:
                continue
            subtotal = book.price * cartitem.quantity
            total += subtotal
            lines.append({"book": book, "qty": cartitem.quantity, "subtotal": subtotal})

        return lines, total
    

        #!checkout--------------------------------------------------------------------------------
    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        # ---- Build cart lines ----
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            flash("Your cart is empty!", "info")
            return redirect(url_for('books_page'))

        cart_lines = []
        total = 0
        for ci in cart_items:
            book = Book.query.get(ci.book_id)
            if not book:
                continue
            qty = ci.quantity or 0
            unit_price = book.price or 0
            subtotal = unit_price * qty
            cart_lines.append({"book": book, "qty": qty, "subtotal": subtotal})
            total += subtotal

        addresses = Address.query.filter_by(user_id=current_user.id).all()

        # ---- GET ----
        if request.method == 'GET':
            return render_template(
                'checkout_page.html',
                css_file='checkout.css',
                cart_lines=cart_lines,
                total=total,
                addresses=addresses,
                selected_pm="Cash"
            )

        # ---- POST ----
        payment_method = request.form.get("payment_method", "Cash")

        # Address: existing or new
                # Either pick an existing address OR create a new one (robust)
        address_id = (request.form.get("address_id") or "").strip()
        address = None

        # 1) If user selected a saved address, use it
        if address_id:
            try:
                address_id_int = int(address_id)
            except ValueError:
                flash("Invalid saved address selected.", "error")
                return render_template(
                    'checkout_page.html',
                    css_file='checkout.css',
                    cart_lines=cart_lines,
                    total=total,
                    addresses=addresses,
                    selected_pm=payment_method
                )

            address = Address.query.filter_by(id=address_id_int, user_id=current_user.id).first()
            if not address:
                flash("Saved address not found for your account.", "error")
                return render_template(
                    'checkout_page.html',
                    css_file='checkout.css',
                    cart_lines=cart_lines,
                    total=total,
                    addresses=addresses,
                    selected_pm=payment_method
                )

        # 2) Otherwise create a new address
        if not address:
            user_fname = request.form.get("user_fname")
            user_lname = request.form.get("user_lname")
            city = request.form.get("city")
            country = request.form.get("country")
            street_line1 = request.form.get("street_line1")
            postal_code = request.form.get("postal_code")
            phone_number = request.form.get("phone_number")

            # IMPORTANT: postal_code is required in your DB
            if not all([user_fname, user_lname, city, country, street_line1, postal_code, phone_number]):
                flash("Please fill all required address fields OR select a saved address.", "error")
                return render_template(
                    'checkout_page.html',
                    css_file='checkout.css',
                    cart_lines=cart_lines,
                    total=total,
                    addresses=addresses,
                    selected_pm=payment_method
                )

            address = Address(
                user_fname=user_fname,
                user_lname=user_lname,
                city=city,
                country=country,
                street_line1=street_line1,
                postal_code=postal_code,
                phone_number=phone_number,
                user_id=current_user.id
            )
            db.session.add(address)
            db.session.flush()

        # address_id = request.form.get("address_id")
        # address = None

        # if address_id:
        #     address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()

        # if not address:
        #     user_fname = request.form.get("user_fname")
        #     user_lname = request.form.get("user_lname")
        #     city = request.form.get("city")
        #     country = request.form.get("country")
        #     street_line1 = request.form.get("street_line1")
        #     postal_code = request.form.get("postal_code")
        #     phone_number = request.form.get("phone_number")

        #     # postal_code is NOT nullable in your model
        #     if not all([user_fname, user_lname, city, country, street_line1, postal_code, phone_number]):
        #         flash("Please fill all required address fields.", "error")
        #         return redirect(url_for('checkout'))

# ==========================================================================================
            # address = Address(
            #     user_fname=user_fname,
            #     user_lname=user_lname,
            #     city=city,
            #     country=country,
            #     street_line1=street_line1,
            #     postal_code=postal_code,
            #     phone_number=phone_number,
            #     user_id=current_user.id
            # )
            # db.session.add(address)
            # db.session.flush()

        # -------------------------
        # CASE 1: CASH (Phase 1 behavior)
        # -------------------------
        if payment_method == "Cash":
            order = Order(
                user_id=current_user.id,
                shipping_address_id=address.id,
                payment_method="Cash",
                total_amount=float(total)
            )
            db.session.add(order)
            db.session.flush()

            for ci in cart_items:
                book = Book.query.get(ci.book_id)
                if not book:
                    continue
                db.session.add(OrderItem(
                    order_id=order.id,
                    book_id=book.id,
                    quantity=ci.quantity,
                    unit_price=float(book.price)
                ))

            # clear cart
            for ci in cart_items:
                db.session.delete(ci)

            db.session.commit()
            return redirect(url_for('order_confirmation', order_id=order.id))

        # -------------------------
        # CASE 2: CARD via Stripe Checkout (Phase 2A)
        # We'll use "Visa" as the value (matches your Enum).
        # -------------------------
        if payment_method not in ("Visa", "Mastercard"):
            flash("Unsupported payment method.", "error")
            return redirect(url_for('checkout'))

        stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        if not stripe_key:
            flash("Stripe is not configured (missing STRIPE_SECRET_KEY).", "error")
            return redirect(url_for('checkout'))

        stripe.api_key = stripe_key


        # stripe_key = os.getenv("STRIPE_SECRET_KEY")
        # if not stripe_key:
        #     flash("Stripe is not configured (missing STRIPE_SECRET_KEY).", "error")
        #     return redirect(url_for('checkout'))

        # stripe.api_key = stripe_key

        # Create Order first (because Payment.order_id is NOT nullable)
        order = Order(
            user_id=current_user.id,
            shipping_address_id=address.id,
            payment_method=payment_method,
            total_amount=float(total)
        )
        db.session.add(order)
        db.session.flush()

        # Add order items (we won't clear cart until payment success)
        for ci in cart_items:
            book = Book.query.get(ci.book_id)
            if not book:
                continue
            db.session.add(OrderItem(
                order_id=order.id,
                book_id=book.id,
                quantity=ci.quantity,
                unit_price=float(book.price)
            ))

        # Create Payment row (Pending)
        payment = Payment(
            amount_paid=float(total),
            status="Pending",
            payment_method=payment_method,
            order_id=order.id,
            user_id=current_user.id
        )
        db.session.add(payment)
        db.session.flush()

        # Build Stripe line items (Stripe uses "smallest currency unit")
        line_items = []
        for line in cart_lines:
            unit_amount = int(round((line["book"].price or 0) * 100))
            line_items.append({
                "price_data": {
                    "currency": "egp",
                    "unit_amount": unit_amount,
                    "product_data": {"name": line["book"].title},
                },
                "quantity": line["qty"]
            })

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            client_reference_id=str(order.id),
            metadata={"order_id": str(order.id), "user_id": str(current_user.id)},
            success_url=url_for('stripe_success', order_id=order.id, _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for('stripe_cancel', order_id=order.id, _external=True),
        )

        # Save gateway references
        payment.transaction_id = session.id
        # session.payment_intent is often present; safe to store if exists
        payment.payment_reference = getattr(session, "payment_intent", None)

        db.session.commit()
        return redirect(session.url, code=303)


    @app.route('/pay/success/<int:order_id>')
    @login_required
    def stripe_success(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            flash("Not allowed.", "error")
            return redirect(url_for('home'))

        session_id = request.args.get("session_id")
        if not session_id:
            flash("Missing payment session.", "error")
            return redirect(url_for('checkout'))

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        if not stripe.api_key:
            flash("Stripe is not configured (missing STRIPE_SECRET_KEY).", "error")
            return redirect(url_for('checkout'))

        session = stripe.checkout.Session.retrieve(session_id)


        # Verify paid + matches this order
        if session.payment_status != "paid":
            flash("Payment not completed.", "error")
            return redirect(url_for('checkout'))

        if str(session.client_reference_id) != str(order_id):
            flash("Payment mismatch.", "error")
            return redirect(url_for('checkout'))

        payment = Payment.query.filter_by(order_id=order_id, user_id=current_user.id).order_by(Payment.id.desc()).first()
        if payment and payment.status != "Success":
            payment.status = "Success"
            payment.transaction_id = session.id
            payment.payment_reference = getattr(session, "payment_intent", payment.payment_reference)

        # Clear cart only after confirmed payment success
        for ci in CartItem.query.filter_by(user_id=current_user.id).all():
            db.session.delete(ci)

        db.session.commit()
        return redirect(url_for('order_confirmation', order_id=order.id))


    @app.route('/pay/cancel/<int:order_id>')
    @login_required
    def stripe_cancel(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            flash("Not allowed.", "error")
            return redirect(url_for('home'))

        # Mark payment failed
        payment = Payment.query.filter_by(order_id=order_id, user_id=current_user.id).order_by(Payment.id.desc()).first()
        if payment and payment.status != "Success":
            payment.status = "Failed"
            payment.failure_reason = "User canceled at payment gateway."
            db.session.commit()

        flash("Payment canceled. Your cart is unchanged.", "info")
        return redirect(url_for('checkout'))

    # @app.route('/checkout', methods=['GET', 'POST'])
    # @login_required
    # def checkout():
    #     cart_lines, total = _get_cart_lines(current_user.id)
    #     if len(cart_lines) == 0:
    #         flash("Your cart is empty!", "info")
    #         return redirect(url_for('books_page'))

    #     addresses = Address.query.filter_by(user_id=current_user.id).all()

    #     if request.method == 'GET':
    #         return render_template(
    #             'checkout_page.html',
    #             css_file='checkout.css',
    #             cart_lines=cart_lines,
    #             total=total,
    #             addresses=addresses
    #         )

    #     # -------------------------
    #     # POST = place COD order
    #     # -------------------------
    #     payment_method = request.form.get("payment_method", "Cash")
    #     if payment_method != "Cash":
    #         flash("For Phase 1 we only support Cash on Delivery.", "info")
    #         return redirect(url_for('checkout'))

    #     # -------------------------
    #     # Address handling (NO JS)
    #     # -------------------------
    #     address_id = (request.form.get("address_id") or "").strip()
    #     address = None

    #     # 1) Use saved address if selected
    #     if address_id:
    #         try:
    #             address_id_int = int(address_id)
    #         except ValueError:
    #             flash("Invalid address selected.", "error")
    #             return redirect(url_for("checkout"))

    #         address = Address.query.filter_by(id=address_id_int, user_id=current_user.id).first()
    #         if not address:
    #             flash("Saved address not found.", "error")
    #             return redirect(url_for("checkout"))

    #     # 2) Otherwise create a new address
    #     else:
    #         user_fname = request.form.get("user_fname")
    #         user_lname = request.form.get("user_lname")
    #         city = request.form.get("city")
    #         country = request.form.get("country")
    #         street_line1 = request.form.get("street_line1")
    #         postal_code = request.form.get("postal_code")
    #         phone_number = request.form.get("phone_number")

    #         # Validate required fields (postal_code is required in your DB model)
    #         if not all([user_fname, user_lname, city, country, street_line1, postal_code, phone_number]):
    #             flash("Please fill all required address fields OR select a saved address.", "error")
    #             return redirect(url_for('checkout'))

    #         address = Address(
    #             user_fname=user_fname,
    #             user_lname=user_lname,
    #             city=city,
    #             country=country,
    #             street_line1=street_line1,
    #             postal_code=postal_code,
    #             phone_number=phone_number,
    #             user_id=current_user.id
    #         )
    #         db.session.add(address)
    #         db.session.flush()  # ensures address.id is available

    #     # -------------------------
    #     # Create Order
    #     # -------------------------
    #     order = Order(
    #         user_id=current_user.id,
    #         shipping_address_id=address.id,
    #         payment_method="Cash",
    #         total_amount=float(total)
    #     )
    #     db.session.add(order)
    #     db.session.flush()  # ensures order.id is available

    #     # -------------------------
    #     # Create Order Items
    #     # -------------------------
    #     cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    #     for cartitem in cart_items:
    #         book = Book.query.get(cartitem.book_id)
    #         if not book:
    #             continue

    #         oi = OrderItem(
    #             order_id=order.id,
    #             book_id=book.id,
    #             quantity=cartitem.quantity,
    #             unit_price=float(book.price or 0)
    #         )
    #         db.session.add(oi)

    #     # -------------------------
    #     # Clear Cart
    #     # -------------------------
    #     for cartitem in cart_items:
    #         db.session.delete(cartitem)

    #     db.session.commit()

    #     return redirect(url_for('order_confirmation', order_id=order.id))

    @app.route('/order-confirmed/<int:order_id>')
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)

        if order.user_id != current_user.id and not current_user.is_admin:
            flash("You are not allowed to view this order.", "error")
            return redirect(url_for('home'))

        items = OrderItem.query.filter_by(order_id=order.id).all()
        lines = []
        for it in items:
            book = Book.query.get(it.book_id)
            lines.append({"book": book, "qty": it.quantity, "unit_price": it.unit_price})

        return render_template("checkout.html",css_file="checkout.css",order=order,order_lines=lines)


    # @app.route('/checkout', methods=['GET', 'POST'])
    # @login_required
    # def checkout():
    #     cart_lines, total = _get_cart_lines(current_user.id)
    #     if len(cart_lines) == 0:
    #         flash("Your cart is empty!", "info")
    #         return redirect(url_for('books_page'))

    #     addresses = Address.query.filter_by(user_id=current_user.id).all()

    #     if request.method == 'GET':
    #         return render_template('checkout_page.html',css_file='checkout.css',cart_lines=cart_lines,total=total,addresses=addresses)

    #     # -------------------------
    #     # POST = place COD order
    #     # -------------------------
    #     payment_method = request.form.get("payment_method", "Cash")
    #     if payment_method != "Cash":
    #         flash("For Phase 1 we only support Cash on Delivery.", "info")
    #         return redirect(url_for('checkout'))

    #     # Either pick an existing address OR create a new one
    #     address_id = request.form.get("address_id")
    #     address = None

    #     if address_id:
    #         address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()

    #     if not address:
    #         user_fname = request.form.get("user_fname")
    #         user_lname = request.form.get("user_lname")
    #         city = request.form.get("city")
    #         country = request.form.get("country")
    #         street_line1 = request.form.get("street_line1")
    #         postal_code = request.form.get("postal_code")
    #         phone_number = request.form.get("phone_number")

    #         if not all([user_fname, user_lname, city, country, street_line1, phone_number]):
    #             flash("Please fill all required address fields.", "error")
    #             return redirect(url_for('checkout'))

    #         address = Address(user_fname=user_fname,user_lname=user_lname,city=city,country=country,street_line1=street_line1, postal_code=postal_code,phone_number=phone_number,user_id=current_user.id)
    #         db.session.add(address)
    #         db.session.flush()

    #     order = Order(user_id=current_user.id,shipping_address_id=address.id,payment_method="Cash",total_amount=float(total))
    #     db.session.add(order)
    #     db.session.flush()

    #     cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    #     for cartitem in cart_items:
    #         book = Book.query.get(cartitem.book_id)
    #         if not book:
    #             continue
    #         oi = OrderItem(order_id=order.id,book_id=book.id,quantity=cartitem.quantity,unit_price=float(book.price))
    #         db.session.add(oi)

    #     for cartitem in cart_items:
    #         db.session.delete(cartitem)

    #     db.session.commit()

    #     return redirect(url_for('order_confirmation', order_id=order.id))

    # @app.route('/order-confirmed/<int:order_id>')
    # @login_required
    # def order_confirmation(order_id):
    #     order = Order.query.get_or_404(order_id)

    #     if order.user_id != current_user.id and not current_user.is_admin:
    #         flash("You are not allowed to view this order.", "error")
    #         return redirect(url_for('home'))

    #     items = OrderItem.query.filter_by(order_id=order.id).all()
    #     lines = []
    #     for it in items:
    #         book = Book.query.get(it.book_id)
    #         lines.append({"book": book, "qty": it.quantity, "unit_price": it.unit_price})

    #     return render_template("checkout.html",css_file="checkout.css",order=order,order_lines=lines)


    @app.route('/seed_db')
    def seed():
        # seed_categories()
        seed_real_books()
        return "Database seeded with real books!"
    

