from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, Member, Product, Round, Order, OrderLine

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def seed_data():
    if Member.query.first():
        return
    m1 = Member(member_no="M-094", name="Ky Tran", phone="0438 601 772")
    m2 = Member(member_no="M-063", name="Jan Buckley", phone="0400 000 000")
    db.session.add_all([m1, m2])

    products = [
        Product(name="Rolled oats, organic", sale_type="weight", price=3.40, bay="B1"),
        Product(name="Brown rice, medium", sale_type="weight", price=4.10, bay="B3"),
        Product(name="Red lentils, split", sale_type="weight", price=4.85, bay="B4"),
        Product(name="Coffee beans, whole", sale_type="weight", price=32.00, bay="C2"),
        Product(name="Tahini, 375 g jar", sale_type="unit", price=9.80, bay="A2"),
        Product(name="Eggs, free range, dozen", sale_type="unit", price=7.50, bay="COOL"),
        Product(name="Olive oil, 1 L tin", sale_type="unit", price=19.60, bay="A1"),
    ]
    db.session.add_all(products)

    r = Round(number=33, status="open")
    db.session.add(r)
    db.session.commit()


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        member_no = request.form.get("member_no")
        member = Member.query.filter_by(member_no=member_no, active=True).first()
        if member:
            session["member_id"] = member.id
            return redirect(url_for("products"))
        flash("Member number not found.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/products")
def products():
    if "member_id" not in session:
        return redirect(url_for("login"))
    r = Round.query.filter_by(status="open").first()
    if not r:
        return render_template("products.html", products=[], round=None)
    prods = Product.query.filter_by(active=True).all()
    return render_template("products.html", products=prods, round=r)


@app.route("/order", methods=["POST"])
def place_order():
    if "member_id" not in session:
        return redirect(url_for("login"))
    r = Round.query.filter_by(status="open").first()
    if not r:
        flash("No open round.")
        return redirect(url_for("products"))

    order = Order.query.filter_by(member_id=session["member_id"], round_id=r.id).first()
    if not order:
        order = Order(member_id=session["member_id"], round_id=r.id)
        db.session.add(order)
        db.session.flush()

    for product in Product.query.filter_by(active=True).all():
        qty_str = request.form.get(f"qty_{product.id}")
        if not qty_str:
            continue
        try:
            qty = float(qty_str)
        except ValueError:
            continue
        if qty <= 0:
            continue
        if product.sale_type == "unit" and qty != int(qty):
            flash(f"{product.name} must be a whole number.")
            continue
        line = OrderLine(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=product.price,
        )
        db.session.add(line)

    db.session.commit()
    return redirect(url_for("my_orders"))


@app.route("/my-orders")
def my_orders():
    if "member_id" not in session:
        return redirect(url_for("login"))
    orders = Order.query.filter_by(member_id=session["member_id"]).all()
    return render_template("my_orders.html", orders=orders)


@app.route("/admin/orders")
def admin_orders():
    orders = Order.query.all()
    return render_template("admin_orders.html", orders=orders)


with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True)