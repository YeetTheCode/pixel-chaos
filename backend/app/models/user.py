from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, FutureDate


class User(BaseModel):
    u: UUID
    name: str
    email: EmailStr = Field(frozen=True)
    on_cooldown: bool = False
    next_placement: FutureDate = None
