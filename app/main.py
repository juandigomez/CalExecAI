"""Main entry point for the AI Calendar Assistant."""

import asyncio
import logging
import warnings

import websockets
from fastmcp import Client

from autogen.io.websockets import IOWebsockets
from autogen.mcp import create_toolkit

from .agents import assistant_agent, execution_agent, groupchat_manager, user_proxy
from .services.calendar_service.mcp import mcp as calendar_service


logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

def on_connect(iostream: IOWebsockets) -> None:
    logger.info(f"[App] - on_connect(): Connected to client using IOWebsockets {iostream}")
    logger.info("[App] - on_connect(): Receiving message from client.")

    async def get_websocket_input(prompt: str):
        return iostream.input()

    initial_msg = iostream.input()
    user_proxy.a_get_human_input = get_websocket_input

    try:
        asyncio.run(chat(initial_msg, iostream))
    except websockets.exceptions.ConnectionClosedOK as e:
        logger.info(f"[App] - Client Disconnected (code={e.code})")
    except Exception as e:
        logger.error(f"[App] - Error in Chat Loop: {e}. Please try again.")


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
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.info(f"[App] - Client Disconnected (code={e.code})")
        except Exception as e:
            logger.error(f"[App] - Error in Chat Loop: {e}. Please try again.")
