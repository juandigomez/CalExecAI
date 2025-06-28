from autogen import (
    AssistantAgent,
    ConversableAgent,
    register_function,
)

from .llms import llm_config
from .tools.datetime import get_current_datetime


assistant_agent = ConversableAgent(
    name="AssistantAgent",
    system_message="""
    You are a helpful AI calendar assistant. Your role is to help users manage their 
    calendar through natural language. You can view calendar events. 
    Always be polite and confirm actions with the user before making any changes to their calendar.
    If you're wondering what day it is, use the get_current_datetime function.

    - When using a tool, defer to the ExecutionAgent.
    
    When asked about these tasks, use your tools rather than just describing what you would do. Don't make assumptions about 
    the user's schedule or preferences without asking first. When you are done, let the user know.
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