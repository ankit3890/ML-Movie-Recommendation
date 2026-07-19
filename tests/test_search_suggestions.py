import pytest
from api.index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search_suggestions_prefix_matching(client):
    """
    Regression test for incorrect substring matching in search suggestions.
    Verifies that suggestions only include titles starting with the query (prefix matching).
    """
    # Setup test data
    global all_titles
    original_all_titles = all_titles
    all_titles = [
        "Man of Steel",
        "Superman",
        "Batman",
        "Wonder Woman",
        "The Matrix",
        "Inception",
        "The Dark Knight",
        "Man in Black"
    ]
    
    try:
        # Test 1: Verify prefix matching works (should pass with fix)
        response = client.get('/api/suggestions?q=man')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 5  # Limited to 5 results
        assert all(title.lower().startswith('man') for title in data)
        assert "Man of Steel" in data
        assert "Man in Black" in data
        assert "Superman" not in data  # Should not match (contains but doesn't start with)
        assert "Batman" not in data    # Should not match (contains but doesn't start with)
        
        # Test 2: Verify empty query returns empty list
        response = client.get('/api/suggestions?q=')
        assert response.status_code == 200
        assert response.get_json() == []
        
        # Test 3: Verify no matches returns empty list
        response = client.get('/api/suggestions?q=nonexistent')
        assert response.status_code == 200
        assert response.get_json() == []
        
        # Test 4: Verify case insensitivity
        response = client.get('/api/suggestions?q=MAN')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 5
        assert all(title.lower().startswith('man') for title in data)
        
        # Test 5: Verify edge case with single character query
        response = client.get('/api/suggestions?q=a')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0  # Should return titles starting with 'a'
        assert all(title.lower().startswith('a') for title in data)
        
        # Test 6: Verify empty all_titles returns empty list
        global all_titles
        all_titles = []
        response = client.get('/api/suggestions?q=man')
        assert response.status_code == 200
        assert response.get_json() == []
        
    finally:
        # Restore original state
        all_titles = original_all_titles