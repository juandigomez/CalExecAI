"""Main entry point for the AI Calendar Assistant."""

import asyncio
import logging
import warnings
from fastmcp import Client

from autogen.mcp import create_toolkit

from .agents import groupchat_manager, assistant_agent, execution_agent, user_proxy
from .services.calendar_service.mcp import mcp as calendar_service
from autogen.io.websockets import IOWebsockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app/logs/server.log"),
        logging.StreamHandler()
    ]
)
warnings.filterwarnings("ignore")


def on_connect(iostream: IOWebsockets) -> None:
    logging.info(f"[App] - on_connect(): Connected to client using IOWebsockets {iostream}")
    logging.info("[App] - on_connect(): Receiving message from client.")

    async def get_websocket_input(prompt: str):
        return iostream.input()

    initial_msg = iostream.input()
    user_proxy.a_get_human_input = get_websocket_input
    asyncio.run(chat(initial_msg, iostream))


async def chat(initial_msg: str, iostream: IOWebsockets):
    async with Client(calendar_service) as client:
        session = client.session
        await session.initialize()

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)
        toolkit.register_for_execution(execution_agent)
        
        try:
            # Initiate the chat with the manager
            await user_proxy.a_initiate_chat(
                groupchat_manager,
                message=initial_msg,
            )
            
        except Exception as e:
            logging.error(f"[App] - Error in Chat Loop: {e}. Please try again.")
