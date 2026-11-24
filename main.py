from flask import Flask, render_template, request, url_for, flash, redirect, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_bootstrap import Bootstrap5
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import os
import stripe
from stripe import StripeClient
from dotenv import load_dotenv




class Base(DeclarativeBase):
    pass


app = Flask(__name__, static_folder='assets', static_url_path="/assets")
@app.route('/ping')
def ping():
    return "ok"

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

bootstrap = Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mobiles.db'

db = SQLAlchemy(model_class = Base)
db.init_app(app)

load_dotenv()
stripe.api_key = os.environ.get('STRIPE_SECRET_API')


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))


class Mobile(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name :Mapped[str] = mapped_column(String, nullable = False)
    price :Mapped[int] = mapped_column(Integer, nullable =False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class Charger(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class Earphone(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class PhoneCase(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)


class PhoneHolder(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable =False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class Camera(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String,
                                             nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class Profile(db.Model):
    id:Mapped[int]=mapped_column(Integer, primary_key=True )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable = False)
    last_name: Mapped[str] = mapped_column(String, nullable = False)
    email: Mapped[str] = mapped_column(String, nullable = False)
    phone: Mapped[str] = mapped_column(String, nullable = False)
    country: Mapped[str] = mapped_column(String, nullable = False)

class Addresses(db.Model):
    id:Mapped[int]=mapped_column(Integer, primary_key=True )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    contact_name: Mapped[str] = mapped_column(String, nullable = False )
    contact_number: Mapped[int]=mapped_column(Integer, nullable = False )
    pincode : Mapped[int]=mapped_column(Integer, nullable = False )
    address : Mapped[str] = mapped_column(String, nullable = False )
    locality:  Mapped[str] = mapped_column(String, nullable = False )
    city: Mapped[str] = mapped_column(String, nullable = False )

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_address: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password : Mapped[str] = mapped_column(String, nullable= False)

class Cart(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

class Wishlist(db.Model):
    id : Mapped[int] =  mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

class RegisterForm(FlaskForm):
    email_address = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired()])
    agree = BooleanField("I agree to the Terms of Use", validators=[DataRequired()])
    submit = SubmitField("Create an account")

class LoginForm(FlaskForm):
    email_address = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

CATEGORY_MODELS = {
    "mobiles": Mobile,
    "cameras": Camera,
    "chargers": Charger,
    "earphones": Earphone,
    "phonecases": PhoneCase,
    "phoneholders": PhoneHolder,
}
total_price = 0

@app.context_processor
def inject_counts():
    wishlist_count = 0
    cart_list_count = 0
    if current_user.is_authenticated:
        wishlist_count = db.session.execute(
            db.select(func.count(Wishlist.id)).where(Wishlist.user_id == current_user.id)
        ).scalar()

        cart_list_count = db.session.execute(db.select(func.count(Cart.id)).where(Cart.user_id == current_user.id)).scalar()
    return dict(wishlist_count=wishlist_count, cart_list_count=cart_list_count)

@app.context_processor
def off_canvas_cart():
    global total_price
    rows = db.session.execute(db.select(Cart).where(Cart.user_id == current_user.id)).scalars().all()

    items = []
    for row in rows:
        product = db.session.get(CATEGORY_MODELS[row.category], row.product_id)
        product_image = product.image_url
        product_price = product.price
        total_price += product_price
        if product:
            items.append(
                {"product": product.name, "quantity": row.quantity, "category": row.category, "image_url": product_image,
                 "price": product_price})

    return dict(cart_items=items, total_price=total_price)





with app.app_context():
    db.create_all()

@app.route('/')
def index():
    result = db.session.execute(db.select(Mobile))
    all_mobiles = result.scalars().all()


    return render_template("index.html", all_mobiles = all_mobiles)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email_address.data.lower().strip()
        result = db.session.execute(db.select(User).where(User.email_address == email))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!", "warning")
            return redirect(url_for('login'))

        given_password = form.password.data
        confirm_password = form.confirm_password.data


        if given_password == confirm_password:
            hash_and_salted_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
            new_user = User(
                email_address = email,
                password = hash_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("index"))

        else:
            flash("Please check if your confirm password is same as your password")

    return render_template("auth-register.html", form = form)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email_address.data.lower().strip()
        user_password= login_form.password.data
        result = db.session.execute(db.select(User).where(User.email_address == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please register.")
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, user_password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('index'))
    return render_template("auth-login.html", form  = login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



@app.route('/about')
def about() -> str:
    return render_template("about-us.html")

@app.route('/contact')
def contact():
    return render_template("contact-us.html")

@app.route('/shop')
def shop_grid_categories():
    return render_template("shop-grid-catgories.html")



@app.route('/shop_list_mobiles')
def shop_list_mobiles():
    result = db.session.execute(db.select(Mobile))
    all_mobiles = result.scalars().all()
    return render_template("shop-list-ofcanvas-filter.html", all_mobiles=all_mobiles)

@app.route('/shop_list_charger')
def shop_list_charger():
    result = db.session.execute(db.select(Charger))
    all_chargers = result.scalars().all()
    return render_template("shop-list-of-canvas-filter-charger.html", all_chargers=all_chargers)

@app.route('/shop_list_earphones')
def shop_list_earphones():
    result = db.session.execute(db.select(Earphone))
    all_earphones = result.scalars().all()
    return render_template("shop-list-of-canvas-filter-earphones.html", all_earphones=all_earphones)

@app.route('/shop_list_phonecase')
def shop_list_phonecase():
    result = db.session.execute(db.select(PhoneCase))
    all_phone_cases = result.scalars().all()
    return render_template("shop-list-of-canvas-filter-phonecase.html", all_phone_cases=all_phone_cases)

@app.route('/shop_list_camera')
def shop_list_camera():
    result = db.session.execute(db.select(Camera))
    all_cameras = result.scalars().all()
    return render_template("shop-list-of-canvas-filter-camera.html", all_cameras=all_cameras)

@app.route('/shop_list_phoneholder')
def shop_list_phoneholder():
    result = db.session.execute(db.select(PhoneHolder))
    all_phoneholders = result.scalars().all()
    return render_template("shop-list-of-canvas-filter-phoneholder.html", all_phoneholders=all_phoneholders)

@app.route('/product-detail/<category>/<int:product_id>', methods=['GET', 'POST'])
def product_detail(category, product_id):
    table = CATEGORY_MODELS[category]
    product = db.session.execute(db.select(table).where(product_id == table.id)).scalar()

    return render_template("product-detail.html", product=product, category = category)



@app.route('/account-addresses', methods=['GET', 'POST'])
@login_required
def account_addresses():
    user_address = db.session.execute(db.select(Addresses).where(Addresses.user_id == current_user.id))
    if request.method == "POST":
        delete_id = request.form.get("delete_address_id")
        address_id = request.form.get("address_id")
        if delete_id:
            addr = Addresses.query.filter_by(id=delete_id, user_id=current_user.id).first()
            if addr:
                db.session.delete(addr)
                db.session.commit()
                flash('Address deleted.', 'success')
        else:
            if address_id:  # edit
                addr = Addresses.query.filter_by(id=address_id, user_id=current_user.id).first()
            else:  # add
                addr = Addresses(user_id=current_user.id)
                db.session.add(addr)

            user_address = Addresses(
                contact_name = request.form["contact"],
                contact_number = request.form["mobileno"],
                pincode= request.form["pincode"],
                address= request.form["address"],
                locality=  request.form["locality"],
                city = request.form["city"]
        )
            db.session.add(user_address)
            db.session.commit()
            flash("Profile saved.")
        return redirect(url_for("account_addresses"))

    addresses = Addresses.query.filter_by(user_id=current_user.id).all()
    return render_template("account-addresses.html", addresses=addresses)


@app.route('/account-my-profile', methods = ['GET', 'POST'])
@login_required
def account_my_profile():
    profile = db.session.execute(db.select(Profile).where(Profile.user_id == current_user.id)).scalar()

    if request.method == "POST":
        profile = Profile(user_id= current_user.id, first_name=request.form["fname"], last_name=request.form["lname"],
                          email=request.form["email"], phone=request.form["phone"],
                          country=request.form["selectcountry"])
        db.session.add(profile)
        db.session.commit()
        flash("Profile saved.")
        return redirect(url_for("account_my_profile"))

    return render_template("account-my-profile.html", profile = profile)



@app.route('/account-wishlist-added/<category>/<int:product_id>', methods=['POST'])
@login_required
def add_wishlist(category, product_id):
    model = CATEGORY_MODELS.get(category)  # the class, e.g. Mobile
    if model is None:
        abort(404)


    product = model.query.get_or_404(product_id)
    # product_quantity = product.quantity


    item = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product.id,        # use the id, not `model`
        category=category,
        image_url = product.image_url
    ).first()

    if not item:
        db.session.add(Wishlist(user_id=current_user.id,
                                product_id=product.id,
                                category=category,
                                quantity = 1,
                                image_url=product.image_url
                                ))
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/add-to-cart/<category>/<int:product_id>', methods = ['POST'])
@login_required
def add_to_cart(product_id, category):
    model = CATEGORY_MODELS.get(category)
    if model is None:
        abort(404)

    item =  db.session.execute(db.select(Cart).where(
            Cart.user_id == current_user.id,
            Cart.category == category,
            Cart.product_id == product_id)).scalar()

    if item:
        item.quantity += 1
    else:
        db.session.add(Cart(user_id=current_user.id, category=category, product_id=product_id))

    try:
        db.session.commit()
        flash("Added to cart.", "success")
    except Exception:
        db.session.rollback()
        flash("Something went wrong, please try again.", "danger")

    return redirect(request.referrer)

@app.route('/update-cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    row = db.session.get(Cart, cart_id)
    if row is None or row.user_id != current_user.id:
        abort(404)

    action = request.form.get('action')
    if action == 'inc':
        row.quantity += 1
    elif action == 'dec':
        row.quantity -= 1
    else:
        try:
            row.quantity = int(request.form.get('quantity', row.quantity))
        except ValueError:
            pass

    if row.quantity < 1:
        db.session.delete(row)
    db.session.commit()
    return redirect(url_for('shopping_cart'))

@app.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    row = db.session.get(Cart, cart_id)
    if row is None or row.user_id != current_user.id:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return redirect(url_for('shopping_cart'))

@app.route('/shopping-cart')
@login_required
def shopping_cart():
    rows = db.session.execute(db.select(Cart).where(Cart.user_id == current_user.id)).scalars().all()
    items = []
    subtotal = 0

    for row in rows:

        product = db.session.get(CATEGORY_MODELS[row.category], row.product_id)

        if not product:
            continue

        line_total = product.price * row.quantity
        subtotal += line_total

        items.append(
            { "id": row.id,"product": product.name, "quantity": row.quantity, "category": row.category,
             "image_url": product.image_url,
             "price": product.price, "line_total": line_total})

    discount = 2232 if items else 0
    shipping = 1488 if items else 0
    total = subtotal - discount + shipping

    if not items:
        flash("Add products to cart", "call to action")

    return render_template("shopping-cart.html", items=items, subtotal=subtotal, total=total, discount=discount,
                           shipping=shipping)

@app.route('/account-wishlist')
@login_required
def account_wishlist():
    rows = db.session.execute(db.select(Wishlist).where(Wishlist.user_id == current_user.id)).scalars().all()
    items = []


    for row in rows:
        product = db.session.get(CATEGORY_MODELS[row.category], row.product_id)
        product_price = product.price


        if product:
            items.append(
                { "product_id" : product.id, "product": product.name, "quantity": row.quantity, "category": row.category, "image_url": product.image_url,
                 "price": product_price})


    if not items:
        flash("Add products to wishlist.", "call to action")

    return render_template("account-wishlist.html", items=items)




def get_cart_items():
    rows = db.session.execute(db.select(Cart). where(Cart.user_id == current_user.id)).scalars().all()
    items = []
    subtotal = 0
    for row in rows:
        product = db.session.get(CATEGORY_MODELS[row.category], row.product_id)
        if not product:
            continue
        line_total = product.price * row.quantity
        subtotal += line_total
        items.append({
            "id": row.id, "product": product.name, "quantity": row.quantity,
            "category": row.category, "image_url": product.image_url,
            "price": product.price, "line_total": line_total,
        })
    return items, subtotal

@app.route('/checkout')
@login_required
def checkout():
    items, subtotal = get_cart_items()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('shopping_cart'))

    addresses = db.session.execute(
        db.select(Addresses).where(Addresses.user_id == current_user.id)
    ).scalars().all()

    shipping = 1488
    total = subtotal + shipping

    return render_template('checkout.html', items=items, addresses=addresses,
                           subtotal=subtotal, shipping=shipping, total=total)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    items, subtotal = get_cart_items()          # helper from the checkout step
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('shopping_cart'))

    # the delivery address chosen on the checkout page
    address_id = request.form.get('address_id', '')
    address = db.session.get(Addresses, int(address_id)) if address_id.isdigit() else None
    if address is None or address.user_id != current_user.id:
        flash("Please choose a delivery address.", "warning")
        return redirect(url_for('checkout'))

    # one Stripe line item per cart product (amounts are in paise)
    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {'name': item['product']},
                'unit_amount': int(item['price']) * 100,
            },
            'quantity': item['quantity'],
        })

    # shipping as its own line
    shipping = 1488
    line_items.append({
        'price_data': {
            'currency': 'inr',
            'product_data': {'name': 'Shipping'},
            'unit_amount': shipping * 100,
        },
        'quantity': 1,
    })

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('checkout', _external=True),
            client_reference_id=str(current_user.id),
            metadata={'address_id': str(address_id)},
        )
    except stripe.error.StripeError as e:
        flash(f"Could not start payment: {e.user_message or 'please try again.'}", "danger")
        return redirect(url_for('checkout'))

    return redirect(checkout_session.url, code=303)

if __name__ == '__main__':
    app.run(debug = True, port = 5001)