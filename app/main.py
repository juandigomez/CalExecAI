"""Main entry point for the AI Calendar Assistant."""

from fastmcp import Client
from fastapi import WebSocket

from autogen.mcp import create_toolkit

from .agents import groupchat_manager, assistant_agent, execution_agent, user_proxy
from .services.calendar_service.mcp import mcp as calendar_service


async def run_calendar_assistant(user_input: str, websocket: WebSocket) -> str:


    async with Client(calendar_service) as client:
        session = client.session
        await session.initialize()

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)
        toolkit.register_for_execution(execution_agent)
        
        try:
            user_proxy.send_text = websocket.receive_text
            groupchat_manager.websocket = websocket
            # Initiate the chat with the manager
            await user_proxy.a_initiate_chat(
                groupchat_manager,
                message=user_input,
            )
            
        except Exception as e:
            print(f"🔹 Error: {e}. Please try again.")


# if __name__ == "__main__":
#     required_vars = ["OPENAI_API_KEY", "MCP_SERVER_URL", "MCP_API_KEY"]
#     missing_vars = [var for var in required_vars if not os.getenv(var)]

#     if missing_vars:
#         print("Error: The following required environment variables are missing:")
#         for var in missing_vars:
#             print(f"- {var}")
#         print(
#             "\nPlease create a .env file with these variables or set them in your environment."
#         )
#     else:
#         asyncio.run(main(), debug=True)
