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


@app.route("/admin/products")
def admin_products():
    products = Product.query.order_by(Product.name).all()
    return render_template("admin_products.html", products=products)

@app.route("/admin/members")
def admin_members():
    members = Member.query.order_by(Member.member_no).all()
    return render_template("admin_members.html", members=members)


@app.route("/admin/members/new", methods=["GET", "POST"])
def admin_member_new():
    if request.method == "POST":
        member_no = request.form.get("member_no", "").strip()
        name = request.form.get("name", "").strip()
        if not member_no or not name:
            flash("Member number and name are required.")
            return redirect(url_for("admin_member_new"))
        if Member.query.filter_by(member_no=member_no).first():
            flash("Member number already exists.")
            return redirect(url_for("admin_member_new"))
        m = Member(member_no=member_no, name=name,
                   phone=request.form.get("phone", "").strip(),
                   email=request.form.get("email", "").strip(), active=True)
        db.session.add(m)
        db.session.commit()
        flash(f"Member '{name}' added.")
        return redirect(url_for("admin_members"))
    return render_template("member_form.html", member=None)


@app.route("/admin/members/<int:member_id>/edit", methods=["GET", "POST"])
def admin_member_edit(member_id):
    m = db.session.get(Member, member_id)
    if not m:
        flash("Member not found.")
        return redirect(url_for("admin_members"))
    if request.method == "POST":
        m.name = request.form.get("name", m.name).strip() or m.name
        m.phone = request.form.get("phone", m.phone).strip()
        m.email = request.form.get("email", m.email).strip()
        db.session.commit()
        flash(f"Member '{m.name}' updated.")
        return redirect(url_for("admin_members"))
    return render_template("member_form.html", member=m)


@app.route("/admin/members/<int:member_id>/toggle", methods=["POST"])
def admin_member_toggle(member_id):
    m = db.session.get(Member, member_id)
    if m:
        m.active = not m.active
        db.session.commit()
        flash(f"Member '{m.name}' is now {'active' if m.active else 'deactivated'}.")
    return redirect(url_for("admin_members"))


@app.route("/admin/products/new", methods=["GET", "POST"])
def admin_product_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.")
            return redirect(url_for("admin_product_new"))
        try:
            price = float(request.form.get("price"))
        except (TypeError, ValueError):
            flash("Price must be a number.")
            return redirect(url_for("admin_product_new"))
        sale_type = request.form.get("sale_type", "unit")
        if sale_type not in ("unit", "weight"):
            sale_type = "unit"
        p = Product(name=name, price=price, sale_type=sale_type,
                    bay=request.form.get("bay", "").strip(), active=True)
        db.session.add(p)
        db.session.commit()
        flash(f"Product '{name}' added.")
        return redirect(url_for("admin_products"))
    return render_template("product_form.html", product=None)


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
def admin_product_edit(product_id):
    p = db.session.get(Product, product_id)
    if not p:
        flash("Product not found.")
        return redirect(url_for("admin_products"))
    if request.method == "POST":
        p.name = request.form.get("name", p.name).strip() or p.name
        try:
            p.price = float(request.form.get("price", p.price))
        except (TypeError, ValueError):
            flash("Price must be a number.")
            return redirect(url_for("admin_product_edit", product_id=p.id))
        st = request.form.get("sale_type")
        if st in ("unit", "weight"):
            p.sale_type = st
        p.bay = request.form.get("bay", p.bay).strip()
        db.session.commit()
        flash(f"Product '{p.name}' updated.")
        return redirect(url_for("admin_products"))
    return render_template("product_form.html", product=p)


@app.route("/admin/products/<int:product_id>/toggle", methods=["POST"])
def admin_product_toggle(product_id):
    p = db.session.get(Product, product_id)
    if p:
        p.active = not p.active
        db.session.commit()
        flash(f"Product '{p.name}' is now {'available' if p.active else 'withdrawn'}.")
    return redirect(url_for("admin_products"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)

