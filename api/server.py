# server.py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asyncio import create_task
from contextlib import asynccontextmanager
from autogen.io.websockets import IOWebsockets
from app.main import on_connect

@asynccontextmanager
async def run_websocket_server(app):
    with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8001) as uri:
        print(f"Websocket server started at {uri}.", flush=True)

        yield

app = FastAPI(lifespan=run_websocket_server)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with chrome-extension://<id> in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/ws/chat")
async def get_chat():
    return FileResponse(os.path.join("frontend", "popup.html"))
