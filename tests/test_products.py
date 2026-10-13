import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Product, Round

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_products.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # 准备数据
            db.session.add(Member(member_no='M-001', name='Test', active=True))
            db.session.add(Product(name='Available Oats', sale_type='weight', price=3.40, active=True))
            db.session.add(Product(name='Withdrawn Item', sale_type='unit', price=5.00, active=False))
            db.session.add(Round(number=99, status='open'))
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()

def test_view_products_open_round(client):
    with client.session_transaction() as sess:
        sess['member_id'] = 1
        
    response = client.get('/products')
    
    # 开放轮次下应该看到可用产品，看不到停用产品
    assert b'Available Oats' in response.data
    assert b'Withdrawn Item' not in response.data

def test_view_products_no_open_round(client):
    r = Round.query.first()
    r.status = 'closed'
    db.session.commit()
    
    with client.session_transaction() as sess:
        sess['member_id'] = 1
        
    response = client.get('/products')
    # 没有开放轮次时，应该渲染空列表并提示，而不是崩溃
    assert b'No open round' in response.data or response.status_code == 200