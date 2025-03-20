import os

from fastapi import APIRouter

from app.core.config import settings
from app.models.user import User

router = APIRouter()


@router.post("/users/", response_model=User)
async def create_user(user: User):
    # Debug logging to understand the environment
    print(
        f"Environment variables: MONGODB_URL="
        f"{os.environ.get('MONGODB_URL', 'Not set')}",
        flush=True,
    )
    print(f"Settings object: mongodb_url={settings.mongodb_url}", flush=True)
    print(f"Creating user at {settings.mongodb_url}", flush=True)
    return await user.insert()
