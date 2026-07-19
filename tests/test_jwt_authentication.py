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
    This test should fail before the patch was applied.
    """
    # Test that protected endpoint is accessible without token (should fail after fix)
    response = client.get('/api/random')
    assert response.status_code == 401  # Should require authentication
    
    # Test that login endpoint exists (should fail before fix)
    response = client.post('/login', data=json.dumps({'username': 'admin', 'password': 'secret'}), content_type='application/json')
    assert response.status_code == 404  # Endpoint didn't exist before fix

def test_jwt_authentication_works_after_fix(client):
    """
    Test that verifies the JWT authentication implementation works correctly.
    This test should pass after the patch was applied.
    """
    # Test successful login
    login_response = client.post('/login', 
                                data=json.dumps({'username': 'admin', 'password': 'secret'}),
                                content_type='application/json')
    assert login_response.status_code == 200
    assert 'access_token' in login_response.get_json()
    
    token = login_response.get_json()['access_token']
    
    # Test protected endpoint with valid token
    protected_response = client.get('/api/random', 
                                   headers={'Authorization': f'Bearer {token}'})
    assert protected_response.status_code == 200
    
    # Test protected endpoint without token
    unauthorized_response = client.get('/api/random')
    assert unauthorized_response.status_code == 401
    
    # Test refresh token endpoint
    refresh_response = client.post('/refresh', 
                                  headers={'Authorization': f'Bearer {token}'})
    assert refresh_response.status_code == 200
    assert 'access_token' in refresh_response.get_json()

def test_jwt_authentication_edge_cases(client):
    """
    Test edge cases for JWT authentication implementation.
    """
    # Test login with invalid credentials
    response = client.post('/login', 
                          data=json.dumps({'username': 'wrong', 'password': 'credentials'}),
                          content_type='application/json')
    assert response.status_code == 401
    
    # Test login with missing JSON
    response = client.post('/login', 
                          data='not json',
                          content_type='text/plain')
    assert response.status_code == 400
    
    # Test login with missing fields
    response = client.post('/login', 
                          data=json.dumps({'username': 'admin'}),
                          content_type='application/json')
    assert response.status_code == 401
    
    # Test protected endpoint with invalid token
    response = client.get('/api/random', 
                         headers={'Authorization': 'Bearer invalid.token.here'})
    assert response.status_code == 401
    
    # Test protected endpoint with expired token (simulated)
    expired_token = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYwOTgzODQwMCwianRpIjoiZjQwYjQwYjQtYjQwYi00YjQwLWI0YjQtYjQwYjQwYjQwYjQwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNjA5ODM4NDAwLCJleHAiOjE2MDk4Mzg0MDAsImNyaXRlc3RyaW5nIjp0cnVlfQ.invalid')
    response = client.get('/api/random', 
                         headers={'Authorization': f'Bearer {expired_token}'})
    assert response.status_code == 401