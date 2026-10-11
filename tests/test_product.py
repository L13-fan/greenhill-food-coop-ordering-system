# US11 verification
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_greenhill.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_admin_product_new(client):
    response = client.post('/admin/products/new', data={
        'name': 'Test Oats',
        'price': '5.50',
        'sale_type': 'weight',
        'bay': 'B1'
    }, follow_redirects=True)
    
    # 直接断言数据库里有没有创建成功
    product = Product.query.filter_by(name='Test Oats').first()
    assert product is not None
    assert product.price == 5.50
    assert product.sale_type == 'weight'

def test_admin_product_toggle(client):
    p = Product(name='To Toggle', price=10.0, sale_type='unit', active=True)
    db.session.add(p)
    db.session.commit()
    
    response = client.post(f'/admin/products/{p.id}/toggle', follow_redirects=True)
    updated_product = db.session.get(Product, p.id)
    assert updated_product.active == False