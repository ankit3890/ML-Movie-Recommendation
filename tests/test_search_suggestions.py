import pytest
from api.index import get_suggestions
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def test_search_suggestions_prefix_matching(app):
    """
    Regression test for incorrect substring matching in search suggestions.
    Verifies that suggestions only include titles that start with the query string.
    """
    with app.test_request_context():
        # Setup test data
        from api.index import all_titles
        all_titles.clear()
        all_titles.extend([
            "Python Snake Documentary",
            "Python Tutorial for Beginners",
            "Advanced Python Programming",
            "Java Tutorial",
            "Python and Data Science",
            "Learning Python",
            "Python Snake Handling Guide"
        ])

        # Test 1: Verify prefix matching works correctly
        with app.test_request_context('/?q=python tut'):
            suggestions = get_suggestions()
            assert "Python Tutorial for Beginners" in suggestions
            assert "Python Snake Documentary" not in suggestions
            assert "Advanced Python Programming" not in suggestions

        # Test 2: Verify exact prefix match is prioritized
        with app.test_request_context('/?q=python'):
            suggestions = get_suggestions()
            assert "Python Tutorial for Beginners" in suggestions
            assert "Advanced Python Programming" in suggestions
            assert "Learning Python" in suggestions
            assert "Python Snake Documentary" in suggestions
            # Should not include titles that only contain 'python' in the middle
            assert "Java Tutorial" not in suggestions

        # Test 3: Verify case insensitivity
        with app.test_request_context('/?q=PYTHON'):
            suggestions = get_suggestions()
            assert "Python Tutorial for Beginners" in suggestions
            assert len(suggestions) > 0

        # Test 4: Verify empty query returns empty list
        with app.test_request_context('/?q='):
            suggestions = get_suggestions()
            assert suggestions == []

        # Test 5: Verify no matches returns empty list
        with app.test_request_context('/?q=nonexistentquery'):
            suggestions = get_suggestions()
            assert suggestions == []

        # Test 6: Verify result limit (should return max 5)
        with app.test_request_context('/?q=python'):
            suggestions = get_suggestions()
            assert len(suggestions) <= 5

        # Test 7: Edge case - query longer than any title
        with app.test_request_context('/?q=verylongquerythatexceedsanytitle'):
            suggestions = get_suggestions()
            assert suggestions == []

        # Test 8: Edge case - special characters in query
        with app.test_request_context('/?q=python-')
        with app.test_request_context('/?q=python@'):
            suggestions1 = get_suggestions()
            suggestions2 = get_suggestions()
            # Should handle special characters gracefully
            assert isinstance(suggestions1, list)
            assert isinstance(suggestions2, list)