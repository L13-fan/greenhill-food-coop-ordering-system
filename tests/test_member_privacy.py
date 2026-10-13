import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member, Round, Order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_privacy.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # 准备测试数据：成员1和成员2，一个轮次
            db.session.add(Member(member_no='M-001', name='Member One', active=True))
            db.session.add(Member(member_no='M-002', name='Member Two', active=True))
            db.session.add(Round(number=99, status='open'))
            db.session.commit()
            
            yield client
            db.session.remove()
            db.drop_all()

def test_member_cannot_see_others_orders(client):
    # 1. 成员1 登录并下单
    with client.session_transaction() as sess:
        sess['member_id'] = 1
    client.post('/order', data={'qty_1': '1'})  # 假设产品ID为1
    
    # 2. 成员2 登录，查看自己的订单
    with client.session_transaction() as sess:
        sess['member_id'] = 2
    response = client.get('/my-orders', follow_redirects=True)
    
    # 3. 断言：成员2的页面里，绝对看不到成员1的订单数据
    # 假设页面里会显示成员编号或订单ID，这里简单断言页面不包含成员1的信息
    assert b'M-001' not in response.data
    assert b'Member One' not in response.data

def test_member_cannot_access_admin_orders(client):
    # 1. 成员1（非协调员）登录
    with client.session_transaction() as sess:
        sess['member_id'] = 1
    
    # 2. 尝试访问协调员专属页面
    response = client.get('/admin/orders', follow_redirects=True)
    
    # 3. 断言：被拒绝访问，并跳转回自己的订单页
    assert b'Access denied' in response.data or b'My Orders' in response.data