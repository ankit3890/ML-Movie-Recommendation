import pytest
from api.index import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_jwt_authentication_missing_before_fix(client):
    """
    Regression test to verify that JWT authentication was missing before the fix.
    This test would fail before the patch was applied.
    """
    # Before the fix, there was no JWT authentication
    # This test verifies that the endpoints exist but aren't protected
    response = client.get('/api/protected')
    # Before fix: should return 200 (no protection)
    # After fix: should return 401 (requires JWT)
    assert response.status_code == 401, "Protected endpoint should require authentication after fix"

def test_jwt_login_endpoint(client):
    """
    Test the JWT login endpoint functionality.
    """
    # Test missing JSON
    response = client.post('/api/login', data={})
    assert response.status_code == 400
    assert b'Missing JSON in request' in response.data
    
    # Test invalid credentials
    response = client.post('/api/login', 
                          data=json.dumps({'username': 'wrong', 'password': 'wrong'}),
                          content_type='application/json')
    assert response.status_code == 401
    assert b'Bad username or password' in response.data
    
    # Test valid credentials
    response = client.post('/api/login',
                          data=json.dumps({'username': 'admin', 'password': 'secret'}),
                          content_type='application/json')
    assert response.status_code == 200
    assert b'access_token' in response.data
    
    # Verify token is in response
    token_data = json.loads(response.data)
    assert 'access_token' in token_data

def test_jwt_protected_endpoint(client):
    """
    Test that the protected endpoint requires valid JWT token.
    """
    # First try without token
    response = client.get('/api/protected')
    assert response.status_code == 401
    
    # Get a valid token
    login_response = client.post('/api/login',
                                data=json.dumps({'username': 'admin', 'password': 'secret'}),
                                content_type='application/json')
    token = json.loads(login_response.data)['access_token']
    
    # Now try with valid token
    response = client.get('/api/protected',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert b'Hello admin!' in response.data
    
    # Try with invalid token
    response = client.get('/api/protected',
                         headers={'Authorization': 'Bearer invalid.token.here'})
    assert response.status_code == 401

def test_jwt_token_structure(client):
    """
    Test that the JWT token contains expected claims.
    """
    login_response = client.post('/api/login',
                                data=json.dumps({'username': 'admin', 'password': 'secret'}),
                                content_type='application/json')
    token = json.loads(login_response.data)['access_token']
    
    # In a real test, you would decode and verify the token claims
    # For this example, we just verify the token exists and is non-empty
    assert token
    assert isinstance(token, str)
    assert len(token) > 10