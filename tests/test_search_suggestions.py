import pytest
import json
from api.index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search_suggestions_endpoint_missing(client):
    """Test that verifies the bug existed before the fix (missing endpoint)"""
    # This test would fail before the fix was applied
    response = client.get('/api/suggestions?q=test')
    assert response.status_code == 404, "Endpoint should not exist before fix"

def test_search_suggestions_endpoint_exists(client):
    """Test that verifies the endpoint exists after the fix"""
    response = client.get('/api/suggestions?q=test')
    assert response.status_code == 200, "Endpoint should exist after fix"

def test_search_suggestions_returns_correct_data(client):
    """Test that verifies the endpoint returns correct suggestion data"""
    # Test with a query that should match some titles
    response = client.get('/api/suggestions?q=avengers')
    data = json.loads(response.data)
    
    assert isinstance(data, list), "Response should be a list"
    assert len(data) > 0, "Should return some suggestions"
    assert all(isinstance(item, str) for item in data), "All items should be strings"
    
    # Verify suggestions contain the query string (case-insensitive)
    assert any('avengers' in item.lower() for item in data), "Suggestions should contain query string"

def test_search_suggestions_empty_query(client):
    """Test edge case with empty query"""
    response = client.get('/api/suggestions?q=')
    data = json.loads(response.data)
    
    assert isinstance(data, list), "Response should be a list"
    assert len(data) <= 5, "Should limit results to 5 even for empty query"

def test_search_suggestions_no_matches(client):
    """Test edge case with no matching titles"""
    response = client.get('/api/suggestions?q=nonexistentmovie12345')
    data = json.loads(response.data)
    
    assert isinstance(data, list), "Response should be a list"
    assert len(data) == 0, "Should return empty list for no matches"

def test_search_suggestions_case_insensitive(client):
    """Test that suggestions are case-insensitive"""
    # Test with different cases
    response1 = client.get('/api/suggestions?q=AVENGERS')
    response2 = client.get('/api/suggestions?q=avengers')
    response3 = client.get('/api/suggestions?q=Avengers')
    
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    data3 = json.loads(response3.data)
    
    # All should return the same results
    assert data1 == data2 == data3, "Results should be case-insensitive"

def test_search_suggestions_max_results(client):
    """Test that results are limited to 5 suggestions"""
    # Create a query that would match many titles
    response = client.get('/api/suggestions?q=a')
    data = json.loads(response.data)
    
    assert len(data) <= 5, "Should limit results to 5 suggestions"
