import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Welcome' in response.data.decode()  # Assuming 'Welcome' is part of the home page text

def test_register_route(client):
    """Test that the register page loads correctly."""
    response = client.get('/register')
    assert response.status_code == 200

def test_login_route(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Login' in response.data.decode()  # Assuming 'Login' is part of the login page text