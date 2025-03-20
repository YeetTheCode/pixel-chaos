from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic_extra_types.color import RGBA
from datetime import datetime

from beanie import Document
from pydantic_extra_types.color import Color


class Pixel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    color: Color = Field(frozen=True)


class Canvas(BaseModel):
    pixels_dict: dict[tuple[int, int], Pixel] = Field(default_factory=dict)
    rows: int = Field(default=100, frozen=True)
    cols: int = Field(default=100, frozen=True)

    def update_pixel(self, pixel: Pixel):
        """Update a pixel in the canvas in O(1) time"""
        self.pixels_dict[(pixel.x, pixel.y)] = pixel

    def get_pixel(self, x: int, y: int) -> Pixel:
        """Get a pixel at the specified coordinates in O(1) time"""
        return self.pixels_dict.get((x, y))

    def get_all_pixels(self):
        """Get all pixels as a list"""
        return list(self.pixels_dict.values())


class CanvasHistory(Document):
    pixel: Pixel
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "canvas_history"
        bson_encoders = {
            # This tells Beanie to convert Color objects to strings when saving
            Color: str
        }
