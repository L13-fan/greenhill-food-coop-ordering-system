# US18 - Round state management (Review verification)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import Round

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_round.db'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_admin_create_round(client):
    response = client.post('/admin/rounds/new', data={'number': '101'}, follow_redirects=True)
    r = Round.query.filter_by(number=101).first()
    assert r is not None
    assert r.status == 'open'

def test_admin_change_round_status(client):
    r = Round(number=102, status='open')
    db.session.add(r)
    db.session.commit()

    # 关闭轮次
    response = client.post(f'/admin/rounds/{r.id}/status/closed', follow_redirects=True)
    updated_r = db.session.get(Round, r.id)
    assert updated_r.status == 'closed'

    # 标记为已打包
    response = client.post(f'/admin/rounds/{r.id}/status/packed', follow_redirects=True)
    updated_r = db.session.get(Round, r.id)
    assert updated_r.status == 'packed'