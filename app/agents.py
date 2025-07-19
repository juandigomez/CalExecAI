import os
import asyncio
from fastapi import WebSocket

from autogen import (
    AssistantAgent,
    ConversableAgent,
    GroupChat,
    GroupChatManager,
)

from .llms import llm_config
from .services.memory_service.memory import MemoryService

async def async_input(prompt: str = " ") -> str:
    return await asyncio.to_thread(input, prompt)

class WebUserProxyAgent(ConversableAgent):
    def __init__(self, send_text: callable = None, send_agent_response: callable = None, **kwargs):
        super().__init__(**kwargs)
        self.send_text = send_text
        self.send_agent_response = send_agent_response

    async def a_get_human_input(self, prompt: str) -> str:
        return await self.send_text()

class WebGroupChatManager(GroupChatManager):
    def __init__(self, websocket: WebSocket=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket = websocket

    async def a_receive(self, message, sender, groupchat, receiver):
        # Intercept assistant responses
        try:
            # Check that it's a dictionary and from assistant
            if isinstance(message, dict) and message.get("role") == "assistant" and message.get("content"):
                await self.websocket.send_text(message["content"])
            elif isinstance(message, str) and sender.name == "AssistantAgent" and message:
                await self.websocket.send_text(message)
        except Exception as e:
            print(f"❌ Error sending assistant message: {e}")

        return await super().a_receive(message, sender, groupchat, receiver)

assistant_agent = ConversableAgent(
    name="AssistantAgent",
    system_message="""
    You are a helpful AI calendar assistant. Your role is to help users manage their 
    calendar through natural language. You can view calendar events.
    Never ask the user what day it is. Always use your tools to find the current datetime.
    Use today's date to make judgements about what day it is tomorrow, for instance.

    Always use your tools rather than just describing what you would do. 
    Don't make assumptions about the user's schedule or preferences without asking first.
    When you are done, let the user know.
    
    - When using a tool, defer to the ExecutionAgent.
    - The following context should be useful to you when you need to remember anything:{context}
    """,
    llm_config=llm_config,
)

execution_agent = AssistantAgent(
    name="ExecutionAgent",
    system_message="""
    Your role is to execute the tools that are suggested to you, and return the results.
    You communicate with the Assistant Agent, so that they can summarize the results of your tool calls.
    """,
    llm_config=llm_config,
)

user_proxy = ConversableAgent(
    name="UserProxy",
    human_input_mode="ALWAYS",
    llm_config=False,
    code_execution_config=False,
)

user_proxy.a_get_human_input = async_input


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
    max_round=20,  # TODO: Bump this way up when not doing dev work
)

# Create Group Chat Manager
groupchat_manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)

assistant_agent.register_hook(
    hookable_method="update_agent_state",
    hook=MemoryService.get_instance().retreive_conversation_history,
)

assistant_agent.register_hook(
    hookable_method="process_last_received_message",
    hook=MemoryService.get_instance().log_conversation_to_mem0,
)

user_proxy.register_hook(
    hookable_method="process_last_received_message",
    hook=MemoryService.get_instance().log_conversation_to_mem0,
)
