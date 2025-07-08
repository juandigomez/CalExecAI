from dotenv import load_dotenv
from typing import Dict, Any
from mem0 import MemoryClient
import os

load_dotenv()

class MemoryService:
    _instance = None

    def __init__(self):
        pass

    async def log_conversation_to_mem0(self, message: Dict[str, Any]):
        # Save each message with metadata
        MemoryService.get_instance().add(
            messages=[{"role": message["role"], "content": message["content"]}],
            user_id="user")

    @classmethod
    def get_instance(cls) -> 'MemoryService':
        """Get the singleton instance of the MemoryService."""
        if cls._instance is None:
            cls._instance = MemoryClient(api_key=os.getenv("MEM0AI_API_KEY"))
        return cls._instance