"""Tests for the CalendarService class."""
import os
import pytest
from unittest.mock import patch, Mock
from src.calendar_service import CalendarService

@pytest.fixture
def calendar_service():
    """Fixture providing a CalendarService instance with test configuration."""
    with patch.dict(os.environ, {
        "MCP_SERVER_URL": "http://test-server/api",
        "MCP_API_KEY": "test-api-key"
    }):
        return CalendarService()

@patch('requests.get')
def test_get_events_success(mock_get, calendar_service):
    """Test successful retrieval of events."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"events": [{"id": "1", "title": "Test Event"}]}
    mock_get.return_value = mock_response
    
    # Call the method
    events = calendar_service.get_events("2023-01-01", "2023-01-31")
    
    # Assertions
    assert len(events) == 1
    assert events[0]["title"] == "Test Event"
    mock_get.assert_called_once_with(
        "http://test-server/api/events",
        params={"start_date": "2023-01-01", "end_date": "2023-01-31"},
        headers={
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json"
        }
    )

@patch('requests.post')
def test_create_event_success(mock_post, calendar_service):
    """Test successful creation of an event."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "1", "title": "New Event"}
    mock_post.return_value = mock_response
    
    # Test data
    event_data = {
        "title": "New Event",
        "start_time": "2023-01-01T10:00:00",
        "end_time": "2023-01-01T11:00:00"
    }
    
    # Call the method
    result = calendar_service.create_event(event_data)
    
    # Assertions
    assert result["title"] == "New Event"
    mock_post.assert_called_once()
    
@patch('requests.patch')
def test_update_event_success(mock_patch, calendar_service):
    """Test successful update of an event."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "1", "title": "Updated Event"}
    mock_patch.return_value = mock_response
    
    # Call the method
    updates = {"title": "Updated Event"}
    result = calendar_service.update_event("1", updates)
    
    # Assertions
    assert result["title"] == "Updated Event"
    mock_patch.assert_called_once()

@patch('requests.delete')
def test_delete_event_success(mock_delete, calendar_service):
    """Test successful deletion of an event."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response
    
    # Call the method
    result = calendar_service.delete_event("1")
    
    # Assertions
    assert result is True
    mock_delete.assert_called_once()

@patch('requests.get')
def test_get_events_error_handling(mock_get, calendar_service):
    """Test error handling when getting events fails."""
    # Setup mock to raise an exception
    mock_get.side_effect = Exception("Connection error")
    
    # Call the method and verify it handles the error
    events = calendar_service.get_events("2023-01-01", "2023-01-31")
    assert events == []
