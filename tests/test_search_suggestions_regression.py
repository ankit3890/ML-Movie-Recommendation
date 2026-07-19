import pytest
from api.index import get_suggestions

# Mock all_titles for testing
all_titles = [
    "The Matrix",
    "The Matrix Reloaded",
    "The Matrix Revolutions",
    "Inception",
    "Interstellar",
    "The Dark Knight",
    "The Godfather",
    "Pulp Fiction",
    "The Shawshank Redemption",
    "The Lord of the Rings: The Fellowship of the Ring",
    "The Lord of the Rings: The Two Towers",
    "The Lord of the Rings: The Return of the King",
    "The",
    "The Avengers",
    "Avengers: Endgame"
]

@pytest.fixture
def mock_all_titles(monkeypatch):
    import api.index
    monkeypatch.setattr(api.index, 'all_titles', all_titles)
    return api.index.all_titles

def test_bug_regression_search_suggestions(mock_all_titles):
    """
    Regression test for incorrect search suggestions bug.
    Verifies that suggestions are properly ranked by relevance.
    """
    # Test case 1: Query that should match exact starts
    suggestions = get_suggestions('the')
    assert len(suggestions) == 5, "Should return exactly 5 suggestions"
    # Verify that exact starts come first
    assert suggestions[0].lower().startswith('the'), "First suggestion should start with query"
    assert all(s.lower().startswith('the') for s in suggestions[:3]), "Top suggestions should start with query"
    
    # Test case 2: Query that should match exact titles
    suggestions = get_suggestions('matrix')
    assert len(suggestions) == 5
    assert all('matrix' in s.lower() for s in suggestions), "All suggestions should contain query"
    # Verify ranking by position
    assert suggestions[0] == "The Matrix", "Exact match should be first"
    
    # Test case 3: Query that appears in middle of titles
    suggestions = get_suggestions('of')
    assert len(suggestions) == 5
    assert all('of' in s.lower() for s in suggestions), "All suggestions should contain query"
    # Verify that earlier occurrences come first
    assert suggestions[0] == "The Lord of the Rings: The Fellowship of the Ring", "Should prioritize earlier occurrence"
    
    # Test case 4: Empty query
    suggestions = get_suggestions('')
    assert suggestions == [], "Empty query should return empty list"
    
    # Test case 5: Query with no matches
    suggestions = get_suggestions('xyz123')
    assert suggestions == [], "Non-matching query should return empty list"
    
    # Test case 6: Case insensitivity
    suggestions = get_suggestions('THE')
    assert len(suggestions) == 5, "Should be case insensitive"
    assert all('the' in s.lower() for s in suggestions), "Should match case insensitively"
    
    # Test case 7: Partial matches should be ranked lower than exact starts
    suggestions = get_suggestions('the')
    # "The" should not be in top 5 if there are better matches
    assert "The" not in suggestions[:5] or suggestions.index("The") > 4, "Partial match 'The' should be ranked low"

def test_bug_regression_edge_cases(mock_all_titles):
    """
    Edge case tests for search suggestions.
    """
    # Test with very short query
    suggestions = get_suggestions('a')
    assert len(suggestions) <= 5, "Should limit to 5 results"
    
    # Test with query that matches many titles
    suggestions = get_suggestions('the')
    assert len(suggestions) == 5, "Should return exactly 5 when many matches exist"
    
    # Test with query that matches exactly 5 titles
    suggestions = get_suggestions('avengers')
    assert len(suggestions) == 2, "Should return all matches when less than 5"
    
    # Test with query that matches exactly 1 title
    suggestions = get_suggestions('pulp fiction')
    assert len(suggestions) == 1, "Should return single match"
    assert suggestions[0] == "Pulp Fiction", "Should return exact match"
