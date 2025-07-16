# server.py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from asyncio import create_task

from app.main import run_calendar_assistant

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with chrome-extension://<id> in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks = {}

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/ws/chat")
async def get_chat():
    return FileResponse(os.path.join("frontend", "popup.html"))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔹 Received from browser: {data}")

            try:
                if websocket in tasks and not tasks[websocket].done():
                    tasks[websocket].cancel()

                # Start a new task
                tasks[websocket] = create_task(run_calendar_assistant(data, websocket))
            except Exception as e:
                await websocket.send_text(f"❌ Internal Error: {str(e)}")

    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected.")
        
        if websocket in tasks:
            tasks[websocket].cancel()
