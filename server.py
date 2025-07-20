"""Extension Server Calling Calendar Service Entry Point."""

import os
import logging
import warnings
import websockets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from autogen.io.websockets import IOWebsockets

from app.main import on_connect

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


@asynccontextmanager
async def run_websocket_server(_: FastAPI):
    try:
        with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
            logging.info(f"[Server] - Websocket server started at {uri}.")

            yield
    except websockets.exceptions.ConnectionClosedOK as e:
        logging.info(f"[Server] - Client Disconnected (code={e.code})")
    except Exception as e:
        logging.error(f"[Server] - Error running websocket server: {e}")

app = FastAPI(lifespan=run_websocket_server)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.post("/log")
async def receive_log(entry: LogEntry):
    log_func = getattr(logging, entry.level.lower(), logging.info)
    log_func(f"[JavaScript] {entry.message}")
    return {"status": "ok"}