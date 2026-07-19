import pytest
from unittest.mock import patch, MagicMock
from public.script import fetchSuggestions, input, suggestionsList, isSearching

@pytest.fixture
def mock_fetch():
    with patch('public.script.fetch') as mock_fetch:
        yield mock_fetch

@pytest.fixture
def mock_input():
    with patch('public.script.input') as mock_input:
        mock_input.value = MagicMock()
        yield mock_input

@pytest.fixture
def mock_suggestions_list():
    with patch('public.script.suggestionsList') as mock_suggestions_list:
        mock_suggestions_list.classList = MagicMock()
        yield mock_suggestions_list

def test_fetchSuggestions_no_suggestions_when_query_too_short(mock_fetch, mock_input, mock_suggestions_list):
    """Test that no suggestions are fetched when query length is less than 2"""
    mock_input.value.trim.return_value = "a"
    fetchSuggestions("a")
    
    mock_fetch.assert_not_called()
    mock_suggestions_list.classList.add.assert_called_with('hidden')

def test_fetchSuggestions_fetches_suggestions_when_query_valid(mock_fetch, mock_input, mock_suggestions_list):
    """Test that suggestions are fetched when query length is >= 2"""
    mock_input.value.trim.return_value = "test"
    mock_fetch.return_value = MagicMock(
        ok=True,
        json=lambda: {"suggestions": ["test1", "test2"]}
    )
    
    fetchSuggestions("test")
    
    mock_fetch.assert_called_once_with('/api/suggestions?query=test')
    mock_suggestions_list.innerHTML = ''
    mock_suggestions_list.appendChild.assert_any_call(MagicMock(textContent='test1'))
    mock_suggestions_list.appendChild.assert_any_call(MagicMock(textContent='test2'))
    mock_suggestions_list.classList.remove.assert_called_with('hidden')

def test_fetchSuggestions_handles_api_errors(mock_fetch, mock_input, mock_suggestions_list, caplog):
    """Test that API errors are handled gracefully"""
    mock_input.value.trim.return_value = "test"
    mock_fetch.return_value = MagicMock(
        ok=False,
        json=lambda: {"error": "Invalid query"}
    )
    
    fetchSuggestions("test")
    
    assert "Suggestions error:" in caplog.text
    mock_suggestions_list.classList.add.assert_called_with('hidden')

def test_fetchSuggestions_ignores_stale_input(mock_fetch, mock_input, mock_suggestions_list):
    """Test that stale input values are ignored"""
    isSearching = False
    mock_input.value.trim.return_value = "old"
    fetchSuggestions("new")
    
    mock_fetch.assert_not_called()

def test_fetchSuggestions_ignores_search_committed(mock_fetch, mock_input, mock_suggestions_list):
    """Test that suggestions are not fetched when search is committed"""
    isSearching = True
    mock_input.value.trim.return_value = "test"
    fetchSuggestions("test")
    
    mock_fetch.assert_not_called()

def test_suggestion_item_click_updates_input_and_triggers_search(mock_fetch, mock_input, mock_suggestions_list):
    """Test that clicking a suggestion updates input and triggers search"""
    mock_input.value.trim.return_value = "test"
    mock_fetch.return_value = MagicMock(
        ok=True,
        json=lambda: {"suggestions": ["suggestion1"]}
    )
    
    fetchSuggestions("test")
    
    suggestion_item = mock_suggestions_list.appendChild.call_args[0][0]
    assert suggestion_item.textContent == "suggestion1"
    
    # Simulate click
    suggestion_item.click()
    assert mock_input.value == "suggestion1"
    mock_suggestions_list.classList.add.assert_called_with('hidden')