"""Main entry point for the AI Calendar Assistant."""
import os
import json
import autogen
from dotenv import load_dotenv
from typing import Dict, Any
from .services.calendar_service import CalendarService

# Load environment variables first
load_dotenv()

# Configure logging
config_list = [
    {
        'model': 'gpt-4',
        'api_key': os.getenv('OPENAI_API_KEY')
    }
]

# Define agent configurations
llm_config = {
    "config_list": config_list,
    "timeout": 120,
}

# Configure code execution with Rancher Desktop's Docker socket
code_execution_config = {
    "work_dir": "coding",
    "use_docker": False,  # Disable Docker execution by default
    "docker_config": {
        "socket": "/Users/jamesvorder/.rd/docker.sock"  # Rancher Desktop socket path
    }
}

# Create the user proxy agent
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A human admin.",
    code_execution_config=code_execution_config,
    human_input_mode="ALWAYS"
)

# Create the calendar assistant agent
calendar_assistant = autogen.AssistantAgent(
    name="Calendar_Assistant",
    system_message="""You are a helpful AI calendar assistant. Your role is to help users manage their 
    calendar through natural language. You can create, update, delete, and view calendar events. 
    Always be polite and confirm actions with the user before making any changes to their calendar.
    
    Available functions:
    - get_events(start_date: str, end_date: str) -> List[Dict]: Get events within a date range
    - create_event(event_data: Dict) -> Optional[Dict]: Create a new event
    - update_event(event_id: str, updates: Dict) -> Optional[Dict]: Update an existing event
    - delete_event(event_id: str) -> bool: Delete an event
    
    Always use the provided functions to interact with the calendar. Don't make assumptions about 
    the user's schedule or preferences without asking first.""",
    llm_config=llm_config,
)

def main():
    """Main function to run the AI Calendar Assistant."""
    print("\n🤖 Welcome to your AI Calendar Assistant!")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    # Register the calendar service with the assistant
    calendar_service = CalendarService()
    
    # Register functions with the assistant
    @user_proxy.register_for_execution()
    @calendar_assistant.register_for_llm(description="Get events within a date range")
    def get_events(start_date: str, end_date: str) -> str:
        """Get events within a date range."""
        events = calendar_service.get_events(start_date, end_date)
        return json.dumps(events, indent=2) if events else "No events found in the specified date range."
    
    @user_proxy.register_for_execution()
    @calendar_assistant.register_for_llm(description="Create a new calendar event")
    def create_event(event_data: Dict[str, Any]) -> str:
        """Create a new calendar event."""
        result = calendar_service.create_event(event_data)
        return json.dumps(result, indent=2) if result else "Failed to create event."
    
    @user_proxy.register_for_execution()
    @calendar_assistant.register_for_llm(description="Update an existing event")
    def update_event(event_id: str, updates: Dict[str, Any]) -> str:
        """Update an existing calendar event."""
        result = calendar_service.update_event(event_id, updates)
        return json.dumps(result, indent=2) if result else "Failed to update event."
    
    @user_proxy.register_for_execution()
    @calendar_assistant.register_for_llm(description="Delete an event")
    def delete_event(event_id: str) -> str:
        """Delete a calendar event."""
        success = calendar_service.delete_event(event_id)
        return "Event deleted successfully." if success else "Failed to delete event."
    
    # Initialize the chat
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("\n👋 Goodbye!")
            break
            
        # Initiate the chat
        user_proxy.initiate_chat(
            calendar_assistant,
            message=user_input
        )

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'MCP_SERVER_URL', 'MCP_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease create a .env file with these variables or set them in your environment.")
    else:
        main()
