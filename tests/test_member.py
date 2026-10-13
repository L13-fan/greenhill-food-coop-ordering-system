import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Member

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

# 下面是缺失的测试函数，请务必加上！
def test_admin_member_new(client):
    response = client.post('/admin/members/new', data={
        'member_no': 'M-999',
        'name': 'Test User',
        'phone': '0400 000 000',
        'email': 'test@example.com'
    }, follow_redirects=True)
    # 改为直接断言数据库里有没有创建成功
    assert Member.query.filter_by(member_no='M-999').first() is not None

def test_admin_member_toggle(client):
    m = Member(member_no='M-888', name='To Deactivate', active=True)
    db.session.add(m)
    db.session.commit()
    
    response = client.post(f'/admin/members/{m.id}/toggle', follow_redirects=True)
    updated_member = db.session.get(Member, m.id)
    assert updated_member.active == False