"""Main entry point for the AI Calendar Assistant."""

import os
import asyncio
from dotenv import load_dotenv

from fastmcp import Client

from autogen import (
    GroupChat,
    GroupChatManager,
)
from autogen.mcp import create_toolkit

from .llms import llm_config
from .agents import assistant_agent, execution_agent, user_proxy
from .services.calendar_service.mcp import mcp as calendar_service
from .services.memory_service.memory import MemoryService


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
        allow_repeat_speaker=False,
        max_round=10,  # TODO: Bump this way up when not doing dev work
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
        asyncio.run(main(), debug=True)
