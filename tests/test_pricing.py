import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import Product


def test_unit_pricing():
    p = Product(name="Tahini", sale_type="unit", price=9.80)
    assert p.line_total(2) == 19.60


def test_weight_pricing():
    p = Product(name="Oats", sale_type="weight", price=3.40)
    assert p.line_total(1.5) == 5.10


def test_weight_pricing_decimal():
    p = Product(name="Coffee", sale_type="weight", price=32.00)
    assert p.line_total(0.25) == 8.00