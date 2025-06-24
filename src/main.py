"""Main entry point for the AI Calendar Assistant."""
import os
import asyncio
import json
import autogen
from dotenv import load_dotenv
from typing import Dict, Any
from .services.calendar_service import mcp as calendar_service
from .services.calendar_service import get_upcoming_events

import mcp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from autogen import LLMConfig
from autogen.agentchat import AssistantAgent
from autogen.mcp import create_toolkit
from fastmcp import Client

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

# Create the calendar assistant agent
calendar_assistant = AssistantAgent(
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
    is_termination_msg=lambda msg: msg == "exit",
)

async def main():
    async with Client(calendar_service) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        resource_templates = await client.list_resource_templates()
        print(f"Available tools: {tools}")
        print(f"Available resources: {resources}")
        print(f"Available resource templates: {resource_templates}")

        await client.session.initialize()
        toolkit = await create_toolkit(session=client.session)
        toolkit.register_for_llm(calendar_assistant)
        
        print("\n🤖 Welcome to your AI Calendar Assistant!")
        print("Type 'exit' to end the session.\n")

        response = calendar_assistant.run(
            message="",
            user_input=True,
            tools=toolkit.tools,
        )
        response.process()
        print(response.messages)


if __name__ == "__main__":
    required_vars = ['OPENAI_API_KEY', 'MCP_SERVER_URL', 'MCP_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease create a .env file with these variables or set them in your environment.")
    else:
        asyncio.run(main())
