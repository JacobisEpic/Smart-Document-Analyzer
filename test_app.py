import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_route(client):
    """Test that the register page loads correctly."""
    response = client.get('/register')
    assert response.status_code == 200
