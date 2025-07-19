# server.py

import os
import logging
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from autogen.io.websockets import IOWebsockets

from app.main import on_connect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app/logs/server.log"),
        logging.StreamHandler()
    ]
)
warnings.filterwarnings("ignore")

class LogEntry(BaseModel):
    message: str
    level: str = "info"

@asynccontextmanager
async def run_websocket_server(app):
    with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8001) as uri:
        logging.info(f"[Server] - Websocket server started at {uri}.")

        yield

app = FastAPI(lifespan=run_websocket_server)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with chrome-extension://<id> in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.post("/log")
async def receive_log(entry: LogEntry):
    log_func = getattr(logging, entry.level.lower(), logging.info)
    log_func(f"[JavaScript] {entry.message}")
    return {"status": "ok"}

@app.get("/ws/chat")
async def get_chat():
    return FileResponse(os.path.join("frontend", "popup.html"))