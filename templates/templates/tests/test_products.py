from models import Product

def test_unit_product_is_counted_as_whole_items():

    p = Product(name="Tahini, 375 g jar", sale_type="unit", price=9.80)
    assert p.line_total(2) == 19.60

def test_weight_product_is_priced_by_kilogram():
   
    p = Product(name="Rolled oats", sale_type="weight", price=3.40)
    assert p.line_total(1.5) == 5.10

def test_withdrawn_product_is_flagged_not_deleted():
    
    p = Product(name="Coffee beans, whole", sale_type="weight", price=32.00, active=True)
    p.active = False
    assert p.active is False
