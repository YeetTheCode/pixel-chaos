from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic_extra_types.color import RGBA


class Pixel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    color: RGBA = Field(frozen=True)

    @field_serializer("color")
    def serialize_rgba(self, color: RGBA):
        return {"r": color.r, "g": color.g, "b": color.b, "alpha": color.alpha}


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
