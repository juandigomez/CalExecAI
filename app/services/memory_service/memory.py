"""Memory Logging Service."""

import logging
import os
import warnings

from typing import Any, Union

from dotenv import load_dotenv
from mem0 import MemoryClient

from autogen import ConversableAgent
from ..calendar_service.sdk import CalendarSDK

logger = logging.getLogger(__name__)
load_dotenv()

warnings.filterwarnings("ignore")

calendar_sdk = CalendarSDK(
    "credentials.json",
    "token.json",
    scopes=[
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)

class MemoryService:
    _instance = None

    def __init__(self):
        self.memory_client = MemoryClient(api_key=os.getenv("MEM0AI_API_KEY"))
        self.user_name = self._get_user_info() if self._get_user_info() else "user"

    def _get_user_info(self):
        try:
            logger.info("[MemoryService] - Getting user info")
            service = calendar_sdk.user_resource
            user_info = service.userinfo().get().execute()
            return user_info.get("name")
        except Exception as e:
            logger.error(f"[MemoryService] - Error getting user info: {e}")

    def retreive_conversation_history(self,agent: ConversableAgent, messages: list[dict[str, Any]]) -> None:  
        try:
            logger.info(f"[MemoryService] - Retrieving conversation history for {agent.name}")
            relevant_memories = self.memory_client.search(messages[len(messages) - 1]["content"], user_id=self.user_name)
            flatten_relevant_memories = "\n".join([m["memory"] for m in relevant_memories])

            agent.update_system_message(agent.system_message.format(context=flatten_relevant_memories))
        except Exception as e:
            logger.error(f"[MemoryService] - Error retreiving conversation history: {e}")

    def log_conversation_to_mem0(self, message: Union[str, list[dict[str, Any]]]) -> str:
        if isinstance(message, list):
            msg_text = message[-1].get("content")
            role = message[-1].get("role")
        else:
            msg_text = message
            role = "user"
        
        try:
            logger.info(f"[MemoryService] Logging conversation to mem0 for {self.user_name}")
            self.memory_client.add(
                messages=[{"role": role, "content": msg_text}],
                user_id=self.user_name
            )
        except Exception as e:
            logger.error(f"[MemoryService] - Error logging conversation to mem0: {e}")
        
        return message

    @classmethod   
    def get_instance(cls) -> 'MemoryService':
        if cls._instance is None:
            cls._instance = MemoryService()
        return cls._instance