"""Calendar service for interacting with the MCP server."""
import os
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class CalendarService:
    """Handles calendar operations with the MCP server."""
    
    def __init__(self):
        """Initialize the calendar service with MCP server configuration."""
        self.base_url = os.getenv("MCP_SERVER_URL")
        self.api_key = os.getenv("MCP_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_events(self, start_date: str, end_date: str) -> List[Dict]:
        """Retrieve events within a date range.
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of calendar events
        """
        try:
            response = requests.get(
                f"{self.base_url}/events",
                params={"start_date": start_date, "end_date": end_date},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("events", [])
        except requests.RequestException as e:
            print(f"Error fetching events: {e}")
            return []
    
    def create_event(self, event_data: Dict) -> Optional[Dict]:
        """Create a new calendar event.
        
        Args:
            event_data: Dictionary containing event details
            
        Returns:
            Created event data if successful, None otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/events",
                json=event_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating event: {e}")
            return None
    
    def update_event(self, event_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            updates: Dictionary containing fields to update
            
        Returns:
            Updated event data if successful, None otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/events/{event_id}",
                json=updates,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/events/{event_id}",
                headers=self.headers
            )
            return response.status_code == 204
        except requests.RequestException as e:
            print(f"Error deleting event: {e}")
            return False
