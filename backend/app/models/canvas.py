from pydantic import BaseModel, field_serializer, ConfigDict
from pydantic import Field
from pydantic_extra_types.color import RGBA

from app.models.websocket import WebSocketManager


class Pixel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    color: RGBA = Field(frozen=True)

    @field_serializer('color')
    def serialize_rgba(self, color: RGBA):
        return {"r": color.r, "g": color.g, "b": color.b, "alpha": color.alpha}


class Canvas(BaseModel):
    connections: WebSocketManager = WebSocketManager()
    pixels: list[Pixel] = []
    rows: int = Field(default=100, frozen=True)
    cols: int = Field(default=100, frozen=True)

    async def update_pixel(self, pixel: Pixel):
        # Find and update the pixel or add it if it doesn't exist
        for i, p in enumerate(self.pixels):
            if p.x == pixel.x and p.y == pixel.y:
                self.pixels[i] = pixel
                break
        else:
            self.pixels.append(pixel)

        # Instead of directly calling broadcast, we'll use a local function
        # to send to all connections (will be updated in services/canvas.py)
        from app.services.canvas import canvas_service
        await canvas_service.ws_service.broadcast(pixel.model_dump())
