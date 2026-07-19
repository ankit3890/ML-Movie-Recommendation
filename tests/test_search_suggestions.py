import pytest
import re
from api.index import get_suggestions

# Mock data for testing
ALL_TITLES = [
    "The Dark Knight",
    "Star Wars",
    "Dark Souls",
    "The Avengers",
    "Avengers: Endgame",
    "Avatar",
    "The Lord of the Rings",
    "Dark Waters",
    "Dark Phoenix",
    "The Dark Tower"
]

@pytest.fixture(autouse=True)
def mock_all_titles(monkeypatch):
    monkeypatch.setattr('api.index.all_titles', ALL_TITLES)

def test_bug_regression():
    """Test that verifies the original bug where substring matching caused irrelevant suggestions"""
    # Test case 1: 'dark' should not match 'Star Wars: The Dark Knight' (word boundary issue)
    suggestions = get_suggestions('dark')
    assert 'Star Wars' not in suggestions, "Bug: 'dark' incorrectly matched 'Star Wars: The Dark Knight'"
    assert 'Dark Souls' in suggestions, "Should match exact word 'Dark'"
    assert 'Dark Waters' in suggestions, "Should match exact word 'Dark'"
    assert 'Dark Phoenix' in suggestions, "Should match exact word 'Dark'"
    assert 'The Dark Tower' in suggestions, "Should match exact word 'Dark'"
    
    # Test case 2: 'av' should not match 'Avatar' (partial word issue)
    suggestions = get_suggestions('av')
    assert 'Avatar' not in suggestions, "Bug: 'av' incorrectly matched 'Avatar'"
    assert 'The Avengers' in suggestions, "Should match exact word 'Avengers'"
    assert 'Avengers: Endgame' in suggestions, "Should match exact word 'Avengers'"
    
    # Test case 3: Exact matches should still work
    suggestions = get_suggestions('dark knight')
    assert 'The Dark Knight' in suggestions, "Should match exact phrase"
    
    # Test case 4: Case insensitivity should still work
    suggestions = get_suggestions('DARK')
    assert 'Dark Souls' in suggestions, "Should be case insensitive"
    
    # Test case 5: Empty query should return empty list
    suggestions = get_suggestions('')
    assert suggestions == [], "Empty query should return empty list"
    
    # Test case 6: Non-matching query should return empty list
    suggestions = get_suggestions('xyz123')
    assert suggestions == [], "Non-matching query should return empty list"

def test_word_boundary_matching():
    """Test that word boundary matching works correctly for various cases"""
    # Test prefix matching
    suggestions = get_suggestions('ava')
    assert 'The Avengers' in suggestions
    assert 'Avengers: Endgame' in suggestions
    assert 'Avatar' not in suggestions
    
    # Test suffix matching
    suggestions = get_suggestions('ters')
    assert 'The Avengers' in suggestions
    assert 'Avengers: Endgame' in suggestions
    assert 'Dark Waters' not in suggestions
    
    # Test middle word matching
    suggestions = get_suggestions('lord')
    assert 'The Lord of the Rings' in suggestions
    
    # Test multiple word matches
    suggestions = get_suggestions('dark')
    assert len(suggestions) == 4  # Should match all titles with 'Dark' as a word

def test_regex_safety():
    """Test that the regex implementation is safe against injection"""
    # Test with special regex characters
    suggestions = get_suggestions('.*+?^${}()|[]\\')
    assert suggestions == [], "Special regex characters should not cause errors"
    
    # Test with quotes
    suggestions = get_suggestions("' OR 1=1")
    assert suggestions == [], "SQL injection attempts should be handled safely"

def test_performance_limits():
    """Test that the suggestion limit is properly enforced"""
    # Create a large list of titles that all match
    large_titles = [f"Movie {i}" for i in range(100)]
    large_titles.extend([f"Dark Movie {i}" for i in range(100)])
    
    # Mock the all_titles with our large dataset
    import api.index
    original_all_titles = api.index.all_titles
    api.index.all_titles = large_titles
    
    try:
        suggestions = get_suggestions('dark')
        assert len(suggestions) <= 5, "Should return at most 5 suggestions"
        assert all('Dark' in t for t in suggestions), "All suggestions should contain 'Dark'"
    finally:
        api.index.all_titles = original_all_titles