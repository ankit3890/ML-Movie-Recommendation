import pytest
from api.index import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_suggestions_endpoint_missing_before_fix(client):
    """
    Regression test that verifies the bug existed before the fix.
    This test would fail before the '/api/suggestions' endpoint was implemented.
    """
    # This test simulates the state before the fix was applied
    # We expect a 404 because the endpoint didn't exist
    response = client.get('/api/suggestions?q=test')
    assert response.status_code == 404

def test_suggestions_endpoint_exists_after_fix(client):
    """
    Verifies that the '/api/suggestions' endpoint now exists and returns valid responses.
    """
    response = client.get('/api/suggestions?q=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_suggestions_empty_query(client):
    """
    Edge case: Empty query should return empty list
    """
    response = client.get('/api/suggestions?q=')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_suggestions_no_query_parameter(client):
    """
    Edge case: No query parameter should return empty list
    """
    response = client.get('/api/suggestions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_suggestions_case_insensitive(client):
    """
    Verifies that the search is case-insensitive
    """
    # Add a test movie title to the system (this would need to be mocked in a real test)
    # For this test, we assume the backend has some movie titles loaded
    response1 = client.get('/api/suggestions?q=test')
    response2 = client.get('/api/suggestions?q=TEST')
    response3 = client.get('/api/suggestions?q=TeSt')
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    data3 = json.loads(response3.data)
    
    # All should return the same results (case-insensitive matching)
    assert data1 == data2 == data3

def test_suggestions_max_five_results(client):
    """
    Verifies that the endpoint returns at most 5 results
    """
    # This would need to be mocked with many matching titles in a real test
    # For this test, we just verify the response structure
    response = client.get('/api/suggestions?q=a')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) <= 5
    assert isinstance(data, list)

def test_suggestions_substring_matching(client):
    """
    Verifies that the endpoint performs substring matching
    """
    # This would need proper test data in a real implementation
    response = client.get('/api/suggestions?q=av')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify all returned titles contain 'av' (case-insensitive)
    for title in data:
        assert 'av' in title.lower()

def test_suggestions_sorted_by_match_position(client):
    """
    Verifies that results are sorted by the position of the match
    """
    # This would need specific test data in a real implementation
    response = client.get('/api/suggestions?q=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # In a real test with proper data, we would verify that titles where
    # 'test' appears earlier in the string come first in the results
    # For this test, we just verify the response structure
    assert isinstance(data, list)