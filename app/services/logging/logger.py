import os
import logging
import warnings
from pydantic import BaseModel

class Logger():
    def __init__(self):
        pass    

    def setup_logging():
        if not os.path.exists("app/logs"):
            os.makedirs("app/logs")
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("app/logs/server.log", mode="w"),
                logging.StreamHandler()
            ]
        )
        warnings.filterwarnings("ignore")

class LogEntry(BaseModel):
    message: str
    level: str = "info"