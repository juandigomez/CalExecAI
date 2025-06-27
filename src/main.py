"""Main entry point for the AI Calendar Assistant."""

import os
import asyncio
import argparse
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
from autogen.agentchat import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.mcp import create_toolkit
from fastmcp import Client

# Load environment variables first
load_dotenv()

# Configure logging
config_list = [{"model": "gpt-4.1-mini", "api_key": os.getenv("OPENAI_API_KEY")}]

# Define agent configurations
llm_config = {
    "config_list": config_list,
    "timeout": 120,
}

assistant_agent = ConversableAgent(
    name="AssistantAgent",
    system_message="""
    You are a helpful AI calendar assistant. Your role is to help users manage their 
    calendar through natural language. You can view calendar events. 
    Always be polite and confirm actions with the user before making any changes to their calendar.
    
    When asked about these tasks, use your tools rather than just describing what you would do. Don't make assumptions about 
    the user's schedule or preferences without asking first.
    """,
    llm_config=llm_config,
)

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    llm_config=False,
    code_execution_config=False
)

async def main(debug=False):

    async with Client(calendar_service) as client:
        session = client.session
        await session.initialize()

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)
        toolkit.register_for_execution(user_proxy)

        # Create Group Chat with all agents
        groupchat = GroupChat(
            agents=[
                assistant_agent,
                user_proxy,
            ],
            messages=[],
            max_round=5, # Allow more rounds for complex conversations
            speaker_selection_method="round_robin",
        )

        # Create Group Chat Manager
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
        )

        if debug:
            from pydantic.networks import AnyUrl

            results = await session.read_resource(uri=AnyUrl("events://future/1"))
            print(results)
        else:

            # Start the interactive CLI conversation
            while True:
                user_input = input("\n🔹 What would you like to do?: ")

                if user_input.lower() in ["exit", "quit"]:
                    print("🔹 Exiting Calendar Assistant. Goodbye!")
                    break

                try:
                    # Initiate the chat with the manager
                    await user_proxy.a_initiate_chat(
                        manager,
                        message=user_input,
                        max_turns=1  # Limit conversation turns to avoid excessive back-and-forth
                    )
                except Exception as e:
                    print(f"🔹 Error: {e}. Please try again.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    required_vars = ["OPENAI_API_KEY", "MCP_SERVER_URL", "MCP_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"- {var}")
        print(
            "\nPlease create a .env file with these variables or set them in your environment."
        )
    else:
        asyncio.run(main(args.debug), debug=True)
