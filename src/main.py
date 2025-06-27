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
from autogen.agentchat import AssistantAgent,ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
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

    - When using a tool, defer to the ExecutionAgent.
    
    When asked about these tasks, use your tools rather than just describing what you would do. Don't make assumptions about 
    the user's schedule or preferences without asking first. When you are done, let the user know.
    """,
    llm_config=llm_config,    
)

execution_agent = AssistantAgent(
    name="ExecutionAgent",
    system_message="""
    You are a helpful AI calendar assistant. Your role is to execute the given tools.
    """,
    llm_config=llm_config,    
)

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="ALWAYS",
    llm_config=False,
    code_execution_config=False,
)

async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

async def main(debug=False):

    async with Client(calendar_service) as client:
        session = client.session
        await session.initialize()

        user_proxy.a_get_human_input = async_input

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)
        toolkit.register_for_llm(execution_agent)
        toolkit.register_for_execution(execution_agent)

        # Create Group Chat with all agents
        groupchat = GroupChat(
            agents=[
                execution_agent,
                assistant_agent,
                user_proxy,
            ],
            messages=[],
            speaker_selection_method="round_robin",
            max_round=20
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
            user_input = input("\n🔹 What would you like to do?: ")
            try:
                # Initiate the chat with the manager
                await user_proxy.a_initiate_chat(
                    manager,
                    message=user_input, # Limit conversation turns to avoid excessive back-and-forth
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
