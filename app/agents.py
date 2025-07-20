"""Agents Configuration for the AI Calendar Assistant."""

from datetime import datetime

from autogen import (
    AssistantAgent,
    ConversableAgent,
    GroupChat,
    GroupChatManager,
    UserProxyAgent,
)

from .llms import llm_config
from .services.memory_service.memory import MemoryService


assistant_agent = ConversableAgent(
    name="AssistantAgent",
    system_message="""
    You are a helpful AI calendar assistant. Your role is to help users manage their 
    calendar through natural language. You can view calendar events. This conversation
    started at """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """.
    Use the conversation start time to make judgements about referencial questions, such as "what day is it tomorrow?"

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

user_proxy = UserProxyAgent(
    name="UserProxy",
    code_execution_config=False,
)

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
