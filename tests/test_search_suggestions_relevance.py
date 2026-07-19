import pytest
from api.index import get_suggestions
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    return app

def test_search_suggestions_relevance(app):
    """
    Regression test for incorrect search suggestions due to improper filtering and sorting.
    Verifies that suggestions are relevant and properly ranked.
    """
    with app.app_context():
        # Setup test data - simulate all_titles from the application
        from api.index import all_titles
        original_all_titles = all_titles.copy()
        
        # Mock all_titles with test data that would expose the bug
        test_titles = [
            "The Bugs Bunny Show",
            "Bugs Life",
            "A Bug's Life",
            "Debugging for Beginners",
            "Insect World",
            "Buggy McBugface",
            "The Big Bug Theory",
            "Bug in the System"
        ]
        
        # Temporarily replace all_titles with test data
        import api.index
        api.index.all_titles = test_titles
        
        try:
            # Test 1: Verify prefix matching works (bug fix verification)
            with app.test_request_context('/api/suggestions?q=bug'):
                suggestions = get_suggestions()
                suggestions_list = suggestions.json
                
                # Should only return titles that start with "bug"
                assert all(title.lower().startswith('bug') for title in suggestions_list), \
                    f"Expected all suggestions to start with 'bug', got: {suggestions_list}"
                
                # Should include the most relevant titles first
                assert suggestions_list[0] in ["Bugs Life", "Buggy McBugface"], \
                    f"Expected most relevant title first, got: {suggestions_list}"
                
                # Should not include "Debugging for Beginners" or "Insect World"
                assert "Debugging for Beginners" not in suggestions_list, \
                    "Should not match substring in middle of title"
                assert "Insect World" not in suggestions_list, \
                    "Should not match unrelated titles"
            
            # Test 2: Verify empty query returns empty list
            with app.test_request_context('/api/suggestions?q='):
                suggestions = get_suggestions()
                assert suggestions.json == [], "Empty query should return empty list"
            
            # Test 3: Verify no query returns empty list
            with app.test_request_context('/api/suggestions'):
                suggestions = get_suggestions()
                assert suggestions.json == [], "No query should return empty list"
            
            # Test 4: Verify case insensitivity
            with app.test_request_context('/api/suggestions?q=BUG'):
                suggestions = get_suggestions()
                assert len(suggestions.json) > 0, "Case insensitive search should work"
                assert all(title.lower().startswith('bug') for title in suggestions.json), \
                    "Case insensitive search should still match prefixes"
            
            # Test 5: Verify limit of 5 results
            with app.test_request_context('/api/suggestions?q=bug'):
                suggestions = get_suggestions()
                assert len(suggestions.json) <= 5, "Should limit to 5 results"
            
            # Test 6: Edge case - query longer than any title
            with app.test_request_context('/api/suggestions?q=verylongquerythatexceedsanytitle'):
                suggestions = get_suggestions()
                assert suggestions.json == [], "Long query with no matches should return empty list"
            
            # Test 7: Edge case - single character query
            with app.test_request_context('/api/suggestions?q=b'):
                suggestions = get_suggestions()
                assert len(suggestions.json) > 0, "Single character query should return results"
                assert all(title.lower().startswith('b') for title in suggestions.json), \
                    "Single character query should still match prefixes"
        
        finally:
            # Restore original all_titles
            api.index.all_titles = original_all_titles