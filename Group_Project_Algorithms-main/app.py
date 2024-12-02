from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a secure key

users = {
    "pzalba.ieu2023@student.ie.edu": "pelayo123",
    "mdrake.ieu2023@student.ie.edu": "miguel123",
    "example123@gmail.com": "example123"
}
products = {
    "breakfast": {
        "Pancakes": 5.99,
        "Omelette": 6.99,
        "Waffles": 4.99,
        "French Toast": 5.49,
        "Bagel with Cream Cheese": 3.49,
        "Avocado Toast": 7.49,
        "Granola with Yogurt": 4.79,
        "Egg & Cheese Croissant": 3.99
    },
    "lunch": {
        "Burger": 9.99,
        "Salad": 7.99,
        "Chicken Sandwich": 8.49,
        "Veggie Wrap": 6.49,
        "Club Sandwich": 7.99,
        "Caesar Salad": 6.99,
        "Grilled Cheese": 5.49,
        "Turkey Avocado Wrap": 8.99,
        "BLT Sandwich": 6.99
    },
    "coffee": {
        "Latte": 3.99,
        "Espresso": 2.99,
        "Cappuccino": 4.49,

        "Americano": 3.49,
        "Flat White": 4.19,
        "Macchiato": 3.29,
        "Mocha": 4.99,
        "Cold Brew": 3.89
    },
    "snacks": {
        "Chips": 1.99,
        "Cookies": 2.49,
        "Brownie": 2.79,
        "Granola Bar": 1.59,
        "Trail Mix": 2.99,
        "Cupcakes": 3.49,
        "Popcorn": 1.79,
        "Pretzels": 2.29,
        "Chocolate Bar": 1.49
    }
}
cart= {}
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('main_menu'))
    return render_template('homepage.html')
cafeterias = {
    "cafeteria1@example.com": "password123",
    "cafeteria2@example.com": "cafepass456"
}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        if email in users and users[email] == password:
            session['user'] = email
            flash(f"Welcome back, {email}!", "success")
            return redirect(url_for('main_menu'))
        else:
            flash("Incorrect email or password.", "danger")

    return render_template('login.html')
@app.route('/cafeteria_login', methods=['GET', 'POST'])
def cafeteria_login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        if email in cafeterias and cafeterias[email] == password:
            session['cafeteria'] = email
            flash(f"Welcome, {email}! You are logged in as a cafeteria.", "success")
            return redirect(url_for('cafeteria_dashboard'))
        else:
            flash("Incorrect email or password.", "danger")

    return render_template('cafeteria_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        if email in users:
            flash("This email is already registered. Please log in.", "warning")
        else:
            users[email] = password
            session['user'] = email
            flash(f"Welcome, {email}! You are now signed up.", "success")
            return redirect(url_for('main_menu'))

    return render_template('signup.html')

@app.route('/main_menu')
def main_menu():
    if 'user' not in session:
        return redirect(url_for('home'))

    return render_template('mainmenu.html')

@app.route('/products/<category>', methods=['GET', 'POST'])
def products_view(category):
    if 'user' not in session:
        return redirect(url_for('home'))

    if category not in products:
        flash("Invalid category.", "danger")
        return redirect(url_for('main_menu'))

    if request.method == 'POST':
        selected_items = request.form.getlist('selected_items')
        for item in selected_items:
            session['cart'][item] = products[category][item]

        flash("Items added to your cart.", "success")
        return redirect(url_for('cart'))

    return render_template('products.html', category=category, items=products[category])

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if not session['cart']:
            flash("Your cart is empty.", "warning")
        else:
            return redirect(url_for('checkout'))

    return render_template('cart.html', cart=session.get('cart', {}))

@app.route('/past_orders')
def past_orders():
    if 'user' not in session:
        return redirect(url_for('home'))

    # Example past orders (only for initial demo purposes)
    session.setdefault('past_orders', {
        "2023-11-10": [
            {"items": ["Latte", "Bagel with Cream Cheese"], "total_price": 7.48},
            {"items": ["Burger", "Cold Brew"], "total_price": 13.88}
        ],
        "2023-11-15": [
            {"items": ["Pancakes", "Espresso"], "total_price": 8.98}
        ]
    })

    return render_template('past_orders.html', past_orders=session['past_orders'])


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('home'))

    cart_items = session.get('cart', {})
    total_price = sum(cart_items.values())

    if request.method == 'POST':
        if 'remove_item' in request.form:
            # Remove selected item from cart
            item_to_remove = request.form['remove_item']
            if item_to_remove in cart_items:
                del cart_items[item_to_remove]
                session['cart'] = cart_items
                flash(f"Removed {item_to_remove} from your cart.", "info")
                return redirect(url_for('checkout'))
        elif 'checkout' in request.form:
            # Handle order placement
            payment_method = request.form['payment_method']
            pickup_time = request.form['pickup_time']

            order_date = datetime.now().strftime("%Y-%m-%d")
            ordered_items = list(cart_items.keys())

            # Save order to past_orders
            session.setdefault('past_orders', {})
            if order_date not in session['past_orders']:
                session['past_orders'][order_date] = []

            session['past_orders'][order_date].append({
                'items': ordered_items,
                'total_price': total_price
            })

            # Clear the cart after checkout
            session['cart'] = {}
            flash(f"Order placed! Come pick up your order at {pickup_time}.", "success")
            return redirect(url_for('past_orders'))

    return render_template(
        'checkout.html',
        cart=cart_items,
        total=total_price
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.route('/cafeteria_dashboard')
def cafeteria_dashboard():
    if 'cafeteria' not in session:
        return redirect(url_for('home'))

    # Gather all orders sorted by pickup time
    past_orders = session.get('past_orders', {})
    orders = []
    for date, daily_orders in past_orders.items():
        for order in daily_orders:
            orders.append({
                'date': date,
                'items': order['items'],
                'total_price': order['total_price'],
                'pickup_time': order.get('pickup_time', "Not specified")
            })

    # Sort orders by pickup time (assuming pickup_time format: HH:MM)
    orders.sort(key=lambda x: datetime.strptime(x['pickup_time'], "%H:%M") if x[
                                                                                  'pickup_time'] != "Not specified" else datetime.max)

    return render_template('cafeteria_dashboard.html', orders=orders)


# Initialize session variables
@app.before_request
def before_request():
    session.setdefault('cart', {})
    session.setdefault('past_orders', {})

if __name__ == '__main__':
    app.run(debug=True)
