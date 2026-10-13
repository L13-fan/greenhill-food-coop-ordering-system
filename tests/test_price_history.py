import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Product, Round, Order, OrderLine

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_price_history.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # 准备测试数据
            db.session.add(Member(member_no='M-001', name='Test Member', active=True))
            # 产品初始价格为 10.00
            db.session.add(Product(name='Test Oats', sale_type='weight', price=10.00, active=True))
            db.session.add(Round(number=99, status='open'))
            db.session.commit()
            
            yield client
            db.session.remove()
            db.drop_all()

def test_price_is_stored_at_order_time(client):
    # 1. 模拟会员登录
    with client.session_transaction() as sess:
        sess['member_id'] = 1
        
    # 2. 在下单时（此时单价为 10.00）提交订单
    client.post('/order', data={
        'qty_1': '2'  # 买 2 公斤燕麦
    })
    
    # 3. 验证订单已创建，且保存的价格是 10.00
    order = Order.query.first()
    assert order is not None
    line = order.lines[0]
    assert line.unit_price == 10.00
    assert line.line_total == 20.00

def test_price_change_does_not_affect_existing_order(client):
    # 1. 模拟会员登录并下单（此时单价为 10.00）
    with client.session_transaction() as sess:
        sess['member_id'] = 1
    client.post('/order', data={'qty_1': '2'})
    
    # 2. 在订单生成后，修改产品价格为 20.00
    product = Product.query.first()
    product.price = 20.00
    db.session.commit()
    
    # 3. 验证订单里的价格依然是 10.00，总额依然是 20.00
    order = Order.query.first()
    line = order.lines[0]
    assert line.unit_price == 10.00
    assert line.line_total == 20.00
    assert order.total() == 20.00