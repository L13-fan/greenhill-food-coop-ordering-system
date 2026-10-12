import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Product, Round, Order, OrderLine

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_order_edit.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            m = Member(member_no='M-001', name='Test Member', active=True)
            p = Product(name='Oats', sale_type='weight', price=3.40, active=True)
            r = Round(number=99, status='open')
            db.session.add_all([m, p, r])
            db.session.commit()
            # 创建一个初始订单
            o = Order(member_id=m.id, round_id=r.id)
            db.session.add(o)
            db.session.commit()
            db.session.add(OrderLine(order_id=o.id, product_id=p.id, quantity=1.0, unit_price=3.40))
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()

def test_edit_order_success(client):
    with client.session_transaction() as sess:
        sess['member_id'] = 1
    # 修改订单数量为 2.0
    response = client.post('/order/edit/1', data={'qty_1': '2.0'}, follow_redirects=True)
    order = db.session.get(Order, 1)
    assert len(order.lines) == 1
    assert order.lines[0].quantity == 2.0
    assert order.total() == 6.80

def test_edit_order_closed_round(client):
    r = db.session.get(Round, 1)
    r.status = 'closed'
    db.session.commit()
    
    with client.session_transaction() as sess:
        sess['member_id'] = 1
    response = client.post('/order/edit/1', data={'qty_1': '5.0'}, follow_redirects=True)
    order = db.session.get(Order, 1)
    assert order.lines[0].quantity == 1.0 # 没有被修改