import os

from dotenv import load_dotenv
from typing import Any, Union
from mem0 import MemoryClient
from autogen import ConversableAgent

load_dotenv()

class MemoryService:
    _instance = None

    def __init__(self):
        self.memory_client = MemoryClient(api_key=os.getenv("MEM0AI_API_KEY"))

    def retreive_conversation_history(self,agent: ConversableAgent, messages: list[dict[str, Any]]) -> None:  
        try:
            relevant_memories = self.memory_client.search(messages[len(messages) - 1]["content"], user_id="user")
            flatten_relevant_memories = "\n".join([m["memory"] for m in relevant_memories])

            agent.update_system_message(agent.system_message.format(context=flatten_relevant_memories))
        except Exception as e:
            print(f"Error retreiving conversation history: {e}")

    def log_conversation_to_mem0(self, message: Union[str, list[dict[str, Any]]]) -> str:
        if isinstance(message, list):
            msg_text = message[-1].get("content")
            role = message[-1].get("role")
        else:
            msg_text = message
            role = "user"
        
        try:
            self.memory_client.add(
                messages=[{"role": role, "content": msg_text}],
                user_id="user"
            )
        except Exception as e:
            print(f"Error logging conversation to mem0: {e}")
        
        return message

    @classmethod   
    def get_instance(cls) -> 'MemoryService':
        if cls._instance is None:
            cls._instance = MemoryService()
        return cls._instance