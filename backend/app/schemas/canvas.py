from typing import List, Literal

from pydantic import BaseModel

from app.models.canvas import Pixel


class PixelUpdateMessage(BaseModel):
    type: Literal["pixel_update"]
    pixel: Pixel


class InitialStateMessage(BaseModel):
    type: Literal["initial_state"]
    pixels: List[Pixel]
