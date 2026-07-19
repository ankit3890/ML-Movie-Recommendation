import pytest
from api.index import get_suggestions

@pytest.fixture
def mock_all_titles():
    return [
        "The Matrix",
        "Star Wars: The Dark Knight",
        "Inception",
        "The Godfather",
        "Pulp Fiction",
        "The Shawshank Redemption",
        "The Dark Knight Rises",
        "Interstellar",
        "The Lord of the Rings",
        "Fight Club"
    ]

def test_bug_regression_prefix_matching(mock_all_titles, monkeypatch):
    """
    Regression test for incorrect search suggestions due to case-sensitive substring matching.
    Verifies that the fix properly implements prefix matching instead of substring matching.
    """
    # Mock the all_titles list in the module
    import api.index
    monkeypatch.setattr(api.index, 'all_titles', mock_all_titles)

    # Test case 1: Query 'the' should not match 'The Matrix' (substring match) but should match 'The Godfather'
    # With the fix, only titles starting with 'the' should match
    from unittest.mock import Mock
    from flask import Flask
    
    app = Flask(__name__)
    with app.test_request_context('/?q=the'):
        response = get_suggestions()
        suggestions = response.get_json()
        # Should only return titles that start with 'the' (case-insensitive)
        assert 'The Godfather' in suggestions
        assert 'The Matrix' not in suggestions  # Was incorrectly included before fix
        assert 'Star Wars: The Dark Knight' not in suggestions  # Was incorrectly included before fix
        assert 'The Dark Knight Rises' in suggestions
        assert 'The Shawshank Redemption' in suggestions
        assert len(suggestions) <= 5  # Limit check

    # Test case 2: Query 'dark' should not match 'Star Wars: The Dark Knight' (substring match)
    with app.test_request_context('/?q=dark'):
        response = get_suggestions()
        suggestions = response.get_json()
        assert 'Star Wars: The Dark Knight' not in suggestions  # Was incorrectly included before fix
        assert 'The Dark Knight Rises' in suggestions
        assert len(suggestions) <= 5

    # Test case 3: Query 'in' should not match 'Inception' (prefix match should work)
    with app.test_request_context('/?q=in'):
        response = get_suggestions()
        suggestions = response.get_json()
        assert 'Inception' in suggestions
        assert len(suggestions) <= 5

    # Test case 4: Empty query should return empty list
    with app.test_request_context('/?q='):
        response = get_suggestions()
        suggestions = response.get_json()
        assert suggestions == []

    # Test case 5: Query longer than any title should return empty list
    with app.test_request_context('/?q=verylongquerythatexceedsanytitlelength'):
        response = get_suggestions()
        suggestions = response.get_json()
        assert suggestions == []

    # Test case 6: Case insensitivity check
    with app.test_request_context('/?q=THE'):
        response = get_suggestions()
        suggestions = response.get_json()
        assert 'The Godfather' in suggestions
        assert 'The Matrix' not in suggestions
        assert len(suggestions) <= 5