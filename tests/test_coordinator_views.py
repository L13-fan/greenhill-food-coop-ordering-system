import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Product, Round, Order, OrderLine

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_coordinator.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # 准备数据
            m = Member(member_no='M-001', name='Test Member', active=True)
            db.session.add(m)
            p1 = Product(name='Tahini', sale_type='unit', price=9.80, active=True)
            p2 = Product(name='Oats', sale_type='weight', price=3.40, active=True)
            db.session.add_all([p1, p2])
            r = Round(number=99, status='open')
            db.session.add(r)
            db.session.commit()
            
            yield client
            db.session.remove()
            db.drop_all()

def test_admin_round_orders(client):
    # 创建一个订单
    order = Order(member_id=1, round_id=1)
    db.session.add(order)
    db.session.commit()
    
    response = client.get('/admin/rounds/1/orders')
    assert response.status_code == 200
    assert b'Test Member' in response.data

def test_admin_round_totals(client):
    # 创建一个订单，包含按件和按公斤商品
    order = Order(member_id=1, round_id=1)
    db.session.add(order)
    db.session.flush()
    
    line1 = OrderLine(order_id=order.id, product_id=1, quantity=2, unit_price=9.80)
    line2 = OrderLine(order_id=order.id, product_id=2, quantity=1.5, unit_price=3.40)
    db.session.add_all([line1, line2])
    db.session.commit()
    
    response = client.get('/admin/rounds/1/totals')
    assert response.status_code == 200
    # 验证汇总是否正确显示
    assert b'Tahini' in response.data
    assert b'2 items' in response.data
    assert b'Oats' in response.data
    assert b'1.50 kg' in response.data