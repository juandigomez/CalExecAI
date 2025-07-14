# server.py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.main import run_calendar_assistant

app = FastAPI()

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
    return FileResponse(os.path.join("frontend", "chat.html"))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await websocket.receive_text()
        print(f"🔹 Received from browser: {data}")

        try:
            response = await run_calendar_assistant(data, websocket)
            await websocket.send_text(response)

        except Exception as e:
            await websocket.send_text(f"❌ Internal Error: {str(e)}")

    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected.")
