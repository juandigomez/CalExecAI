import os

from autogen import AssistantAgent, ConversableAgent

from .llms import llm_config
from autogen.agentchat.group import OnCondition, StringLLMCondition
from autogen.agentchat.group import AgentTarget


async def async_input(prompt: str = " ") -> str:
    return await asyncio.to_thread(input, prompt)

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
    - The following context should be useful to you when you need to remember anything:
    {context}

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

register_function(
    get_current_datetime,
    caller=assistant_agent,
    executor=execution_agent,
    description=(
        get_current_datetime.__doc__
        if get_current_datetime.__doc__
        else "Get the current date and time."
    ),
)
