import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import WebsocketUrl
from pydantic_extra_types.color import Color
from redis import Redis

from app.api.deps import get_canvas, get_redis, get_ws_manager
from app.models.canvas import Canvas, CanvasHistory, Pixel
from app.models.websocket import WebSocketConnection, WebSocketManager
from app.schemas.canvas import InitialStateMessage, PixelUpdateMessage

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    canvas: Canvas = Depends(get_canvas),
    ws_manager: WebSocketManager = Depends(get_ws_manager),
    redis_client: Redis = Depends(get_redis),
):
    # Connect the client
    await websocket.accept()
    ws_manager.connections[client_id] = WebSocketConnection(
        url=WebsocketUrl(f"ws://localhost:8000/ws/{client_id}"),
        connection=websocket,
        connected=True,
    )

    try:
        # Send entire canvas state as one message
        all_pixels = canvas.get_all_pixels()
        message = InitialStateMessage(type="initial_state", pixels=all_pixels)
        await websocket.send_text(message.model_dump_json())

        # Handle incoming pixel updates
        while True:
            data = await websocket.receive_text()
            await handle_pixel_update(data, canvas, ws_manager, redis_client)

    except WebSocketDisconnect:
        # Expected disconnect, clean up normally
        pass
    except Exception as e:
        # Unexpected error
        print(f"WebSocket error for client {client_id}: {e}", flush=True)
    finally:
        # Clean up the connection in all cases
        if client_id in ws_manager.connections:
            ws_manager.connections[client_id].connected = False
            del ws_manager.connections[client_id]


async def handle_pixel_update(
    data: str, canvas: Canvas, ws_manager: WebSocketManager, redis_client: Redis
):
    """Process incoming pixel update data"""
    print("Updating pixel", flush=True)
    try:
        json_data = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON received: {e}", flush=True)
        return

    try:
        # Convert the color dict to RGB object
        print(json_data["color"], flush=True)
        rgb = (
            json_data["color"].get("r"),
            json_data["color"].get("g"),
            json_data["color"].get("b"),
        )
        json_data["color"] = Color(rgb)
        pixel_data = Pixel.model_validate(json_data)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Invalid pixel data format: {e}", flush=True)
        return
    # Ensure canvas has Redis client
    if not canvas.redis_client:
        canvas.redis_client = redis_client

    # Update canvas
    canvas.update_pixel(pixel_data)

    print("broadcasting pixel update to clients", flush=True)
    # Broadcast to all clients
    await broadcast_pixel_update(pixel_data, ws_manager)
    print("initiating save of history event", flush=True)
    try:
        canvas_history = CanvasHistory(pixel=pixel_data)
        print(canvas_history, flush=True)
        await canvas_history.create()
        print("successfully wrote the pixel", flush=True)
    except Exception as e:
        print(f"Error saving pixel change to database {e}", flush=True)


async def broadcast_pixel_update(pixel: Pixel, ws_manager: WebSocketManager):
    """Send a pixel update to all connected clients"""
    update_pixel_message = PixelUpdateMessage(type="pixel_update", pixel=pixel)
    pixel_update_json = update_pixel_message.model_dump_json()

    # Create a copy of the keys to avoid modification during iteration
    client_ids = list(ws_manager.connections.keys())

    # Skip stale connections
    for client_id in client_ids:
        connection = ws_manager.connections.get(client_id)
        if not connection or not connection.connected:
            continue

        try:
            await connection.connection.send_text(pixel_update_json)
        except (RuntimeError, OSError) as e:
            print(f"Failed to send to client {client_id}: {e}", flush=True)
            # Clean up stale connection
            if client_id in ws_manager.connections:
                ws_manager.connections[client_id].connected = False
                del ws_manager.connections[client_id]
