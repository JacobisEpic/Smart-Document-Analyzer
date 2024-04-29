import pytest
from app import create_app
from flask import session

@pytest.fixture
def register(client, username, password):
    return client.post('/register', data={'username': username, 'password': password}, follow_redirects=True)
