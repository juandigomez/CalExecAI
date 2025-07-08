import os

from dotenv import load_dotenv
from typing import Dict, Any
from mem0 import MemoryClient
from autogen import ConversableAgent

load_dotenv()

class MemoryService:
    _instance = None

    def __init__(self):
        self.memory_client = MemoryClient(api_key=os.getenv("MEM0AI_API_KEY"))

    def retreive_conversation_history(self,agent: ConversableAgent, messages: list[dict[str, Any]]) -> None:        
        relevant_memories = self.memory_client.search(messages[len(messages) - 1]["content"], user_id="user")
        flatten_relevant_memories = "\n".join([m["memory"] for m in relevant_memories])

        agent.update_system_message(agent.system_message.format(context=flatten_relevant_memories))

    async def log_conversation_to_mem0(self, message: Dict[str, Any]):
        self.memory_client.add(
            messages=[{"role": message["role"], "content": message["content"]}],
            user_id="user"
        )

    @classmethod   
    def get_instance(cls) -> 'MemoryService':
        if cls._instance is None:
            cls._instance = MemoryService()
        return cls._instance