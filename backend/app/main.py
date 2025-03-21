from contextlib import asynccontextmanager

import redis
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.routes import canvas, users
from app.core.config import settings
from app.models.canvas import Canvas, CanvasHistory
from app.models.user import User
from app.models.websocket import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(
        settings.mongodb_url,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
    )

    try:
        # Initialize Beanie with our document models
        try:
            await init_beanie(
                database=mongo_client[settings.db_name],
                document_models=[User, CanvasHistory],
            )
            print("Successfully connected to MongoDB and initialized models")
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

        # Store shared application state directly in app.state
        app.state.canvas = Canvas()
        app.state.ws_manager = WebSocketManager()
        # Configure Redis connection
        # In Docker Compose, the service name is used as the hostname
        # Your service is named "redis-stack" in the compose file
        app.state.redis_client = redis.Redis(
            host=settings.redis_host,  # Match the service name in docker-compose.yml
            port=settings.redis_port,  # Default Redis port
            # Automatically decode byte responses to strings
            decode_responses=settings.redis_decode_responses,
            # Add timeout to avoid hanging
            socket_timeout=settings.redis_socket_timeout,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
        )
        # Include routers
        app.include_router(canvas.router, prefix="/api", tags=["canvas"])
        app.include_router(users.router, prefix="/api", tags=["user"])
        yield
    finally:
        # Always close the mongo_client connection
        mongo_client.close()
        app.state.redis_client.close()


# Initialize app
app = FastAPI(title="Canvas API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Canvas API is running"}
