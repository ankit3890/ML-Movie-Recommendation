import pytest
from api.index import get_suggestions
from unittest.mock import patch

@patch('api.index.all_titles', ['Python Tutorial', 'Java Tutorial', 'Python for Beginners', 'Advanced Python', 'Python Cookbook'])
def test_search_suggestions_case_insensitive_relevance():
    # Test case-sensitive substring matching issue
    with app.test_client() as client:
        # Test 1: Basic case insensitivity
        response = client.get('/api/suggestions?q=python')
        data = response.get_json()
        assert response.status_code == 200
        assert len(data) == 5  # Should return all matches
        assert 'Python Tutorial' in data
        assert 'Java Tutorial' not in data  # Should not match unrelated titles
        
        # Test 2: Relevance ordering (query as whole word earlier in title should rank higher)
        response = client.get('/api/suggestions?q=python')
        data = response.get_json()
        assert data[0] == 'Python Tutorial'  # Should be first as 'Python' is first word
        assert data[1] == 'Python for Beginners'
        assert data[2] == 'Advanced Python'
        assert data[3] == 'Python Cookbook'
        
        # Test 3: Partial word matching should still work
        response = client.get('/api/suggestions?q=tutorial')
        data = response.get_json()
        assert len(data) == 2
        assert 'Python Tutorial' in data
        assert 'Java Tutorial' in data
        
        # Test 4: Empty query should return empty list
        response = client.get('/api/suggestions?q=')
        data = response.get_json()
        assert data == []
        
        # Test 5: Non-existent query should return empty list
        response = client.get('/api/suggestions?q=nonexistent')
        data = response.get_json()
        assert data == []
        
        # Test 6: Case variations should match
        response = client.get('/api/suggestions?q=PYTHON')
        data = response.get_json()
        assert len(data) == 4
        assert 'Python Tutorial' in data
        
        # Test 7: Word boundary matching (should not match partial words)
        response = client.get('/api/suggestions?q=thon')
        data = response.get_json()
        assert len(data) == 0  # Should not match 'Python' as it's not a whole word
        
        # Test 8: Multiple word query
        response = client.get('/api/suggestions?q=python tutorial')
        data = response.get_json()
        assert len(data) == 1
        assert 'Python Tutorial' in data