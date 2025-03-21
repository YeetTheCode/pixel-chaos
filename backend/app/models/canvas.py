from datetime import datetime

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.color import Color
from redis import Redis


class Pixel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x: int = Field(frozen=True)
    y: int = Field(frozen=True)
    color: Color = Field(frozen=True)


class Canvas(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    pixels_dict: dict[tuple[int, int], Pixel] = Field(default_factory=dict)
    rows: int = Field(default=100, frozen=True)
    cols: int = Field(default=100, frozen=True)
    redis_client: Redis = None
    redis_key: str = "canvas:pixels"

    def _get_pixels_from_redis(self):
        """Helper method to load pixels from Redis into memory"""
        if not self.redis_client:
            return {}

        try:
            # Get all pixels from Redis
            redis_pixels_data = self.redis_client.hgetall(self.redis_key)
            redis_pixels = {}

            # Parse pixels from Redis
            for coord_key, pixel_json in redis_pixels_data.items():
                try:
                    # Use Pydantic to parse the JSON
                    pixel = Pixel.model_validate_json(pixel_json)
                    redis_pixels[(pixel.x, pixel.y)] = pixel
                except Exception as e:
                    print(
                        f"Error parsing pixel from Redis {coord_key}: {e}", flush=True
                    )

            print(f"Loaded {len(redis_pixels)} pixels from Redis", flush=True)
            return redis_pixels
        except Exception as e:
            print(f"Error loading pixels from Redis: {e}", flush=True)
            return None

    def initialize_from_redis(self, redis_client: Redis):
        """Initialize the canvas from Redis cache if available"""
        # Save Redis connection for future use
        self.redis_client = redis_client

        # Use the helper method to load pixels
        redis_pixels = self._get_pixels_from_redis()

        # Update the in-memory dictionary with loaded pixels
        if redis_pixels is not None:
            self.pixels_dict.clear()  # Clear existing data
            self.pixels_dict.update(redis_pixels)

    def update_pixel(self, pixel: Pixel):
        """Update a pixel in Redis first, then in the in-memory cache"""
        # Always prioritize Redis update
        if self.redis_client:
            try:
                # Use the coordinate as the hash field key
                coord_key = f"{pixel.x}:{pixel.y}"

                # Store pixel as JSON in Redis hash
                self.redis_client.hset(
                    self.redis_key, coord_key, pixel.model_dump_json()
                )
            except Exception as e:
                print(f"Error updating pixel in Redis: {e}", flush=True)

        # Also update in-memory as a backup/cache
        self.pixels_dict[(pixel.x, pixel.y)] = pixel

    def get_pixel(self, x: int, y: int) -> Pixel:
        """Get a pixel at the specified coordinates, always checking Redis first"""
        # Always prioritize Redis
        if self.redis_client:
            try:
                coord_key = f"{x}:{y}"
                pixel_json = self.redis_client.hget(self.redis_key, coord_key)

                if pixel_json:
                    # Let Pydantic handle the parsing
                    pixel = Pixel.model_validate_json(pixel_json)
                    # Update in-memory cache for future quick access
                    self.pixels_dict[(x, y)] = pixel
                    return pixel
            except Exception as e:
                print(f"Error retrieving pixel from Redis: {e}", flush=True)
                # Fall back to in-memory if Redis fails

        # Only use in-memory as a fallback
        return self.pixels_dict.get((x, y))

    def get_all_pixels(self):
        """Get all pixels from Redis primarily, with in-memory as fallback"""
        # Always try Redis first as the source of truth
        if self.redis_client:
            try:
                # Load fresh data from Redis
                redis_pixels = self._get_pixels_from_redis()

                if redis_pixels is not None:
                    # Update our in-memory cache
                    self.pixels_dict.clear()
                    self.pixels_dict.update(redis_pixels)

                    # Return the pixels from Redis
                    return list(redis_pixels.values())
            except Exception as e:
                print(f"Error in get_all_pixels from Redis: {e}", flush=True)
                # Continue with in-memory data if Redis fails

        # Fall back to in-memory only if Redis failed or is unavailable
        print("Using in-memory pixel cache as fallback", flush=True)
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
