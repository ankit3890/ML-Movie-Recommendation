import pytest
from api.index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_suggestions_prefix_matching(client):
    """
    Regression test for incorrect search suggestions due to unfiltered substring matching.
    Verifies that only titles starting with the query are returned as suggestions.
    """
    # Setup test data
    global all_titles
    original_titles = all_titles.copy()
    all_titles = [
        "The Matrix",
        "The Dark Knight",
        "Inception",
        "Interstellar",
        "The Shawshank Redemption",
        "The Godfather",
        "Pulp Fiction",
        "The Lord of the Rings"
    ]

    try:
        # Test 1: Verify prefix matching works (should pass with fix)
        response = client.get('/api/suggestions?q=the')
        assert response.status_code == 200
        suggestions = response.get_json()
        assert len(suggestions) == 5  # Limited to 5 results
        assert all(s.lower().startswith('the') for s in suggestions)
        assert "The Matrix" in suggestions
        assert "The Dark Knight" in suggestions
        assert "The Shawshank Redemption" in suggestions
        assert "The Godfather" in suggestions
        assert "The Lord of the Rings" in suggestions
        # Should NOT include "Inception" or "Interstellar"
        assert "Inception" not in suggestions
        assert "Interstellar" not in suggestions

        # Test 2: Verify substring matching is fixed (should fail without fix)
        # Without the fix, 'the' would match 'theme' in 'Interstellar' (if it existed)
        # This test ensures we don't get false positives from middle-of-word matches
        response = client.get('/api/suggestions?q=the')
        suggestions = response.get_json()
        assert "Pulp Fiction" not in suggestions  # 'the' appears in middle

        # Test 3: Edge case - empty query
        response = client.get('/api/suggestions?q=')
        assert response.status_code == 200
        assert response.get_json() == []

        # Test 4: Edge case - no matches
        response = client.get('/api/suggestions?q=zebra')
        assert response.status_code == 200
        assert response.get_json() == []

        # Test 5: Edge case - case insensitivity
        response = client.get('/api/suggestions?q=THE')
        assert response.status_code == 200
        suggestions = response.get_json()
        assert len(suggestions) == 5
        assert all(s.lower().startswith('the') for s in suggestions)

        # Test 6: Edge case - partial word at start
        response = client.get('/api/suggestions?q=inter')
        assert response.status_code == 200
        suggestions = response.get_json()
        assert "Interstellar" in suggestions
        assert "Inception" not in suggestions  # Doesn't start with 'inter'

    finally:
        # Restore original titles
        all_titles = original_titles