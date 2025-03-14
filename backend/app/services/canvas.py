from app.models.canvas import Canvas, Pixel
from app.services.websocket import WebSocketService


class CanvasService:
    def __init__(self):
        self.ws_service: WebSocketService = WebSocketService()
        self.canvas = Canvas()

    def get_all_pixels(self):
        """Get all pixels from the canvas"""
        return self.canvas.get_all_pixels()

    async def update_pixel(self, pixel: Pixel):
        """Update a pixel and broadcast the change to all clients"""
        self.canvas.update_pixel(pixel)

        # Handle the broadcasting separately in the service layer
        await self.ws_service.broadcast(pixel)


# Create a singleton instance
canvas_service = CanvasService()
