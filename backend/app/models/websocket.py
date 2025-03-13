from typing import Dict

from fastapi import WebSocket
from pydantic import BaseModel, WebsocketUrl, ConfigDict


class WebSocketConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    url: WebsocketUrl
    connection: WebSocket
    connected: bool = False


class WebSocketManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Intentionally not instantiating the default value with factory so the
    # dict acts as a singleton even if multiple models are created by mistake
    connections: Dict[str, WebSocketConnection] = {}
