import pytest
from app import create_app
from pymongo import MongoClient
import mongomock

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE'] = mongomock.MongoClient().db

    with app.test_client() as client:
        yield client

def test_login_successful(client):
    # Assuming there's a function to insert user for the sake of testing
    user = {"username": "testuser", "password": "testpass"}
    client.application.config['DATABASE'].users.insert_one(user)

    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # assuming successful login redirects
    assert 'upload_pdf' in response.location  # assuming redirection to upload_pdf on successful login

def test_login_unsuccessful(client):
    response = client.post('/login', data={'username': 'wronguser', 'password': 'wrongpass'})
    assert response.status_code == 401  # assuming 401 returned on failed login
    assert 'Invalid credentials' in response.data.decode()  # assuming this message is returned on failure
