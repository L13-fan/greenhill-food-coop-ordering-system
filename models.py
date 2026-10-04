from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)

    orders = db.relationship("Order", backref="member", lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sale_type = db.Column(db.String(10), nullable=False)  # "unit" or "weight"
    price = db.Column(db.Float, nullable=False)  # per unit or per kg
    bay = db.Column(db.String(10))
    active = db.Column(db.Boolean, default=True)

    def line_total(self, quantity):
        return round(quantity * self.price, 2)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), default="open")  # open, closed, packed
    close_at = db.Column(db.DateTime)
    pickup_at = db.Column(db.DateTime)

    orders = db.relationship("Order", backref="round", lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey("round.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lines = db.relationship("OrderLine", backref="order", lazy=True, cascade="all, delete-orphan")

    def total(self):
        return round(sum(line.line_total for line in self.lines), 2)


class OrderLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # price at time of order

    product = db.relationship("Product")

    @property
    def line_total(self):
        return round(self.quantity * self.unit_price, 2)