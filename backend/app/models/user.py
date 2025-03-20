from beanie import Document
from pydantic import EmailStr, Field, FutureDate


class User(Document):
    name: str
    email: EmailStr = Field(frozen=True)
    on_cooldown: bool = False
    next_placement: FutureDate = None
