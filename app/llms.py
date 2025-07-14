import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


config_list = [{"model": "gpt-4.1-mini", "api_key": os.getenv("OPENAI_API_KEY")}]

llm_config = {
    "config_list": config_list,
    "timeout": 120,
}
