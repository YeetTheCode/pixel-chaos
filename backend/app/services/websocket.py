import json

from fastapi import WebSocket
from pydantic import WebsocketUrl

from app.models.canvas import Pixel
from app.models.websocket import WebSocketConnection, WebSocketManager
from app.schemas.canvas import PixelUpdateMessage


class WebSocketService:
    def __init__(self):
        self.ws_manager = WebSocketManager()

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection"""
        print(f"Connection attempt from client: {client_id}")
        await websocket.accept()
        print(f"Connection accepted for client: {client_id}")
        self.ws_manager.connections[client_id] = WebSocketConnection(
            url=WebsocketUrl(f"ws://localhost:8000/ws/{client_id}"),
            connection=websocket,
            connected=True,
        )

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.ws_manager.connections:
            self.ws_manager.connections[client_id].connected = False
            del self.ws_manager.connections[client_id]

    async def broadcast(self, pixel: Pixel):
        """Send a message to all connected clients"""
        message = PixelUpdateMessage(type="pixel_update", pixel=pixel)
        json_message = json.dumps(message.model_dump())

        for client_id, connection in list(self.ws_manager.connections.items()):
            if connection.connected:
                try:
                    await connection.connection.send_text(json_message)
                except (RuntimeError, OSError):
                    self.disconnect(client_id)
