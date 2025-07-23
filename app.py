from flask import Flask, render_template, request, redirect, url_for, jsonify
import stripe

app = Flask(__name__)

# 🔑 Your Stripe test secret key
stripe.api_key = "sk_test_51RnySd4eXWnb62cp2x1LdpD2iFQHwo7RvBiRmnfaVcWgglDaoMOGPQSH7VU2lNCalmY65zmLNfUQsniTMy0ISmBJ00tjx6Xdd9"

gold_bars = [
    {"weight": "1g", "price": 300, "image": "1g.jpg"},
    {"weight": "10g", "price": 2900, "image": "10g.jpg"},
    {"weight": "100g", "price": 28000, "image": "100g.jpg"},
]

cart = []

@app.route("/", methods=["GET", "POST"])
def index():
    global cart
    if request.method == "POST":
        if request.form.get("action") == "add_to_cart":
            weight = request.form["weight"]
            for item in gold_bars:
                if item["weight"] == weight:
                    cart.append(item)
                    break
            return redirect(url_for('index'))
    return render_template("index.html", gold_bars=gold_bars)

@app.route("/cart", methods=["GET", "POST"])
def show_cart():
    total = sum(item['price'] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/remove", methods=["POST"])
def remove_from_cart():
    global cart
    index = int(request.form["index"])
    if 0 <= index < len(cart):
        del cart[index]
    return redirect(url_for("show_cart"))

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    line_items = []
    for item in cart:
        line_items.append({
            'price_data': {
                'currency': 'aed',
                'product_data': {
                    'name': f"{item['weight']} Gold Bar"
                },
                'unit_amount': int(item['price']) * 100  # Stripe uses cents
            },
            'quantity': 1,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:5000/success',
        cancel_url='http://127.0.0.1:5000/cart'
    )
    return redirect(session.url, code=303)

@app.route("/success")
def success():
    global cart
    cart.clear()
    return "<h2>✅ Payment Successful! Thank you for your order.</h2>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
