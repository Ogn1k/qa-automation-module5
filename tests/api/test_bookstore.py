import uuid
import pytest
import requests
import allure
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

def test_authorized_empty_credentials(session):
    # Current Swagger documents Authorized, not the Login URL in the handout.
    r = session.post(BASE+'/Account/v1/Authorized', json={'userName':'','password':''}, timeout=30)
    assert r.status_code == 400
    assert r.headers['Content-Type'].startswith('application/json')
    assert r.json()['code'] == '1200'
    assert r.json()['message'] == 'UserName and Password required.'

def test_user_empty(session):
    r = session.post(BASE+'/Account/v1/User', json={'userName':'','password':''}, timeout=30)
    assert r.status_code == 400
    assert r.json()['code'] == '1200'

@pytest.mark.parametrize('password', ['short', 'onlylowercase'])
def test_weak_password(session, password):
    r = session.post(BASE+'/Account/v1/User', json={'userName':'m5_'+uuid.uuid4().hex,'password':password}, timeout=30)
    assert r.status_code == 400
    assert r.json()['code'] == '1300'


@allure.feature('Book Store Account lifecycle')
@allure.severity(allure.severity_level.CRITICAL)
def test_positive_user_lifecycle(session):
    """Create an isolated account, authorize it and always remove it."""
    credentials = {'userName': 'm5_' + uuid.uuid4().hex, 'password': 'M5_Strong_' + uuid.uuid4().hex + '!9aA'}
    user_id = None
    token = None
    try:
        with allure.step('Create a unique user: HTTP 201'):
            response = session.post(BASE + '/Account/v1/User', json=credentials, timeout=30)
            assert response.status_code == 201, response.text
            body = response.json()
            user_id = body['userID']
            assert user_id and body['username'] == credentials['userName']
            assert body['books'] == []
            allure.attach('{"status":201,"books":[]}', 'Create user (credentials omitted)', allure.attachment_type.JSON)
        with allure.step('Generate a token: HTTP 200, status Success'):
            response = session.post(BASE + '/Account/v1/GenerateToken', json=credentials, timeout=30)
            assert response.status_code == 200, response.text
            body = response.json()
            token = body['token']
            assert token and body['status'] == 'Success' and body['expires']
        with allure.step('Authorize valid credentials: HTTP 200, true'):
            response = session.post(BASE + '/Account/v1/Authorized', json=credentials, timeout=30)
            assert response.status_code == 200, response.text
            assert response.json() is True
        with allure.step('Retrieve the created user with Bearer authentication'):
            response = session.get(BASE + '/Account/v1/User/' + user_id,
                                   headers={'Authorization': 'Bearer ' + token}, timeout=30)
            assert response.status_code == 200, response.text
            body = response.json()
            assert body['userId'] == user_id and body['username'] == credentials['userName']
            assert body['books'] == []
    finally:
        if user_id:
            with allure.step('Remove the temporary user: HTTP 204 (cleanup)'):
                if not token:
                    response = session.post(BASE + '/Account/v1/GenerateToken', json=credentials, timeout=30)
                    response.raise_for_status()
                    token = response.json()['token']
                response = session.delete(BASE + '/Account/v1/User/' + user_id,
                                          headers={'Authorization': 'Bearer ' + token}, timeout=30)
                assert response.status_code == 204, 'Temporary user cleanup failed: ' + response.text
