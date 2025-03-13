from app.models.canvas import Pixel, Canvas
from app.services.websocket import WebSocketService


class CanvasService:
    def __init__(self):
        self.ws_service = WebSocketService()
        self.canvas = Canvas()  # Use the Canvas model instead of separate pixels list

    def get_all_pixels(self):
        """Get all pixels from the canvas"""
        return self.canvas.pixels

    async def update_pixel(self, pixel: Pixel):
        """Update a pixel and broadcast the change to all clients"""
        # Update the pixel in the canvas model
        await self.canvas.update_pixel(pixel)


# Create a singleton instance
canvas_service = CanvasService()
