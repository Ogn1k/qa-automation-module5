import uuid
import pytest
import requests
pytestmark = pytest.mark.api
BASE = 'https://demoqa.com'

@pytest.fixture
def session():
    with requests.Session() as s:
        yield s

def test_books(session):
    r = session.get(BASE+'/BookStore/v1/Books', timeout=30)
    assert r.status_code == 200
    books = r.json()['books']
    assert books and all('isbn' in b and 'title' in b for b in books)

def test_login_empty(session):
    r = session.post(BASE+'/Account/v1/Login', json={'userName':'','password':''}, timeout=30)
    assert r.status_code == 400
    assert r.json()['code'] == '1200'

def test_user_empty(session):
    r = session.post(BASE+'/Account/v1/User', json={'userName':'','password':''}, timeout=30)
    assert r.status_code == 400
    assert r.json()['code'] == '1200'

@pytest.mark.parametrize('password', ['short', 'onlylowercase'])
def test_weak_password(session, password):
    r = session.post(BASE+'/Account/v1/User', json={'userName':'m5_'+uuid.uuid4().hex,'password':password}, timeout=30)
    assert r.status_code == 400
    assert r.json()['code'] == '1300'
