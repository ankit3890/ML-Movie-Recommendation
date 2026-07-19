import pytest
from unittest.mock import patch, MagicMock
from public.script import fetchSuggestions

@pytest.fixture
def mock_fetch():
    with patch('public.script.fetch') as mock_fetch:
        yield mock_fetch

def test_fetch_suggestions_makes_api_call(mock_fetch):
    """Test that fetchSuggestions makes an API call to /api/suggestions"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"suggestions": ["test1", "test2"]}
    mock_fetch.return_value = mock_response
    
    # Mock DOM elements
    suggestionsList = MagicMock()
    suggestionsList.innerHTML = ''
    
    # Call the function
    fetchSuggestions("test", suggestionsList)
    
    # Verify API call was made
    mock_fetch.assert_called_once_with('/api/suggestions?query=test')

def test_fetch_suggestions_populates_suggestions(mock_fetch):
    """Test that suggestions are properly displayed in the UI"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"suggestions": ["suggestion1", "suggestion2"]}
    mock_fetch.return_value = mock_response
    
    suggestionsList = MagicMock()
    suggestionsList.innerHTML = ''
    
    fetchSuggestions("query", suggestionsList)
    
    # Verify suggestions were added to the DOM
    assert suggestionsList.innerHTML == ''
    assert len(suggestionsList.appendChild.call_args_list) == 2

def test_fetch_suggestions_handles_empty_response(mock_fetch):
    """Test that empty suggestions are handled gracefully"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"suggestions": []}
    mock_fetch.return_value = mock_response
    
    suggestionsList = MagicMock()
    suggestionsList.innerHTML = ''
    
    fetchSuggestions("query", suggestionsList)
    
    # Should not add any suggestions
    assert suggestionsList.appendChild.call_count == 0

def test_fetch_suggestions_handles_api_error(mock_fetch):
    """Test that API errors are caught and logged"""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.json.return_value = {"error": "Invalid query"}
    mock_fetch.return_value = mock_response
    
    suggestionsList = MagicMock()
    
    # Should not raise an exception
    fetchSuggestions("invalid", suggestionsList)

def test_fetch_suggestions_encodes_query(mock_fetch):
    """Test that special characters in query are properly encoded"""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"suggestions": []}
    mock_fetch.return_value = mock_response
    
    suggestionsList = MagicMock()
    
    fetchSuggestions("test query with spaces & special=chars", suggestionsList)
    
    # Verify the query was properly encoded in the URL
    call_args = mock_fetch.call_args[0][0]
    assert "query=test+query+with+spaces+%26+special%3Dchars" in call_args