from pydantic import BaseModel, field_serializer, ConfigDict
from pydantic import Field
from pydantic_extra_types.color import RGBA


class Pixel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    color: RGBA = Field(frozen=True)

    @field_serializer('color')
    def serialize_rgba(self, color: RGBA):
        return {"r": color.r, "g": color.g, "b": color.b, "alpha": color.alpha}


class Canvas(BaseModel):
    pixels: list[Pixel] = []
    rows: int = Field(default=100, frozen=True)
    cols: int = Field(default=100, frozen=True)

    def update_pixel(self, pixel: Pixel):
        """Update a pixel in the canvas"""
        for i, p in enumerate(self.pixels):
            if p.x == pixel.x and p.y == pixel.y:
                self.pixels[i] = pixel
                return
        self.pixels.append(pixel)
