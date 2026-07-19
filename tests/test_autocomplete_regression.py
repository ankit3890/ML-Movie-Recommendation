import pytest
from api.index import get_suggestions

@pytest.fixture
def mock_all_titles():
    return [
        "The Dark Knight",
        "Inception",
        "The Shawshank Redemption",
        "Pulp Fiction",
        "The Godfather",
        "Fight Club",
        "Forrest Gump",
        "The Matrix",
        "Goodfellas",
        "The Silence of the Lambs"
    ]

def test_case_sensitive_matching_bug(mock_all_titles, monkeypatch):
    """
    Regression test for case-sensitive matching bug in autocomplete.
    Verifies that search suggestions work regardless of query case.
    """
    # Mock the all_titles list in the module
    import api.index
    monkeypatch.setattr(api.index, 'all_titles', mock_all_titles)
    
    # Test with lowercase query - should match all titles containing "the"
    api.index.query = "the"
    response = get_suggestions()
    suggestions = response.get_json()
    
    # Should return 5 suggestions with "The" in title (case-insensitive)
    assert len(suggestions) == 5
    assert all("the" in s.lower() for s in suggestions)
    
    # Test with mixed case query
    api.index.query = "ThE"
    response = get_suggestions()
    suggestions = response.get_json()
    
    # Should still return 5 suggestions
    assert len(suggestions) == 5
    assert all("the" in s.lower() for s in suggestions)
    
    # Test with uppercase query
    api.index.query = "THE"
    response = get_suggestions()
    suggestions = response.get_json()
    
    # Should still return 5 suggestions
    assert len(suggestions) == 5
    assert all("the" in s.lower() for s in suggestions)

def test_relevance_ranking_fix(mock_all_titles, monkeypatch):
    """
    Regression test for relevance ranking in autocomplete.
    Verifies that matches are ordered by position of query substring.
    """
    import api.index
    monkeypatch.setattr(api.index, 'all_titles', mock_all_titles)
    
    # Test query that appears in multiple positions
    api.index.query = "the"
    response = get_suggestions()
    suggestions = response.get_json()
    
    # Verify results are ordered by position of "the" in title
    positions = [s.lower().index("the") for s in suggestions]
    assert positions == sorted(positions), "Suggestions should be ordered by match position"

def test_edge_cases(mock_all_titles, monkeypatch):
    """
    Edge case tests for autocomplete suggestions.
    """
    import api.index
    monkeypatch.setattr(api.index, 'all_titles', mock_all_titles)
    
    # Test empty query
    api.index.query = ""
    response = get_suggestions()
    suggestions = response.get_json()
    assert len(suggestions) == 0, "Empty query should return no suggestions"
    
    # Test query with no matches
    api.index.query = "xyz123"
    response = get_suggestions()
    suggestions = response.get_json()
    assert len(suggestions) == 0, "Non-matching query should return no suggestions"
    
    # Test query that matches exactly 5 items
    api.index.query = "the"
    response = get_suggestions()
    suggestions = response.get_json()
    assert len(suggestions) == 5, "Should return exactly 5 suggestions when available"
    
    # Test query that matches more than 5 items
    # Add more titles with "the" to test truncation
    more_titles = mock_all_titles + [
        "The Terminator",
        "The Truman Show",
        "The Town",
        "The Theory of Everything",
        "The Tourist",
        "The Hangover"
    ]
    monkeypatch.setattr(api.index, 'all_titles', more_titles)
    api.index.query = "the"
    response = get_suggestions()
    suggestions = response.get_json()
    assert len(suggestions) == 5, "Should truncate to 5 suggestions when more than 5 match"
