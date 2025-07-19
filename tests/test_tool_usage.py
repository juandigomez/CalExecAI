import pytest
import json
from fastmcp import Client
from autogen.mcp import create_toolkit

from app.services.calendar_service.mcp import mcp
from app.agents import assistant_agent
from autogen.io.run_response import RunResponseProtocol
from autogen.events import BaseEvent
from autogen.events.agent_events import ToolCallEvent
from autogen.io.processors import EventProcessorProtocol

class ToolUseEventProcessor(EventProcessorProtocol):

    def __init__(self):
        self.tool_calls = []
    
    def process(self, response: RunResponseProtocol) -> None:
        for event in response.events:
            self.process_event(event)

    def process_event(self, event: BaseEvent) -> None:
        if isinstance(event, ToolCallEvent):
            self.tool_calls.append(event.content.tool_calls[0].function.arguments)  # type: ignore
        else:
            pass



@pytest.mark.asyncio
@pytest.mark.parametrize("input,tool_call", [
    ("what are my next 5 meetings?", "events://future/5"),
])
async def test_tool_usage(input: str, tool_call: str):
    async with Client(mcp) as client:
        session = client.session
        await session.initialize()

        toolkit = await create_toolkit(session=session)
        toolkit.register_for_llm(assistant_agent)

        result = assistant_agent.run(
            message=input,
            max_turns=1,
        )

        tool_use_aggregator = ToolUseEventProcessor()
        result.process(processor=tool_use_aggregator)

        assert len(tool_use_aggregator.tool_calls) == 1
        assert json.loads(tool_use_aggregator.tool_calls[0]).get('uri') == tool_call