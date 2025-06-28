"""Main entry point for the AI Calendar Assistant."""

import os
import asyncio
import argparse
from dotenv import load_dotenv

from fastmcp import Client

from autogen import (
    GroupChat,
    GroupChatManager,
)
from autogen.mcp import create_toolkit

from .llms import llm_config
from .agents import assistant_agent, execution_agent, user_proxy
from .services.calendar_service import mcp as calendar_service

# Load environment variables first
load_dotenv()


async def async_input(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)


async def main(debug=False):

    # Create Group Chat with all agents
    groupchat = GroupChat(
        agents=[
            execution_agent,
            assistant_agent,
            user_proxy,
        ],
        messages=[],
        speaker_selection_method="auto",
    )

    # Create Group Chat Manager
    groupchat_manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
    )

    async with Client(calendar_service) as client:
        session = client.session
        await session.initialize()

        user_proxy.a_get_human_input = async_input

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)
        toolkit.register_for_execution(execution_agent)

        if debug:
            from pydantic.networks import AnyUrl

            results = await session.read_resource(uri=AnyUrl("events://future/1"))
            print(results)
        else:
            user_input = input("\n🔹 What would you like to do?: ")
            try:
                # Initiate the chat with the manager
                await user_proxy.a_initiate_chat(
                    groupchat_manager,
                    message=user_input,
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
