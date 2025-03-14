import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.deps import get_canvas_service
from app.models.canvas import RGBA, Pixel
from app.schemas.canvas import InitialStateMessage
from app.services.canvas import CanvasService

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    # Connect the client
    await canvas_service.ws_service.connect(websocket, client_id)
    try:
        # Send entire canvas state as one message
        all_pixels = canvas_service.get_all_pixels()
        message = InitialStateMessage(type="initial_state", pixels=all_pixels)
        await websocket.send_text(json.dumps(message.model_dump()))
        # Handle incoming pixel updates
        while True:
            data = await websocket.receive_text()
            await handle_pixel_update(data, canvas_service)

    except WebSocketDisconnect:
        canvas_service.ws_service.disconnect(client_id)
    except Exception as e:
        print(f"Error: {e}")
        canvas_service.ws_service.disconnect(client_id)


async def handle_pixel_update(data: str, canvas_service: CanvasService):
    """Process incoming pixel update data"""
    try:
        json_data = json.loads(data)
        # Convert the color dict to RGBA object
        json_data["color"] = RGBA(**json_data["color"])
        pixel_data = Pixel.model_validate(json_data)

        # Update canvas and broadcast to all clients
        await canvas_service.update_pixel(pixel_data)
    except Exception as e:
        print(f"Error processing update: {str(e)}")
