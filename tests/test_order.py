import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Product, Round, Order, OrderLine

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_order.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # 准备测试数据
            m = Member(member_no='M-001', name='Test Member', active=True)
            db.session.add(m)
            
            # 按件产品
            p1 = Product(name='Tahini', sale_type='unit', price=9.80, active=True)
            # 按公斤产品
            p2 = Product(name='Oats', sale_type='weight', price=3.40, active=True)
            db.session.add_all([p1, p2])
            
            r = Round(number=99, status='open')
            db.session.add(r)
            db.session.commit()
            
            yield client
            db.session.remove()
            db.drop_all()

def test_place_order_success(client):
    # 模拟会员登录
    with client.session_transaction() as sess:
        sess['member_id'] = 1
        
    # 提交订单（2件Tahini，1.5公斤Oats）
    response = client.post('/order', data={
        'qty_1': '2',    # Tahini
        'qty_2': '1.5'   # Oats
    }, follow_redirects=True)
    
    # 验证订单已创建
    order = Order.query.first()
    assert order is not None
    assert len(order.lines) == 2
    
    # 验证金额计算（2*9.80 + 1.5*3.40 = 19.60 + 5.10 = 24.70）
    assert order.total() == 24.70

def test_place_order_no_round(client):
    # 关闭所有轮次
    r = Round.query.first()
    r.status = 'closed'
    db.session.commit()
    
    with client.session_transaction() as sess:
        sess['member_id'] = 1
        
    response = client.post('/order', data={'qty_1': '1'}, follow_redirects=True)
    # 应该提示没有开放的轮次，且不会创建订单
    assert b'No open round' in response.data
    assert Order.query.count() == 0