import redis
from fastapi.requests import HTTPConnection


async def get_canvas(connection: HTTPConnection):
    """
    Get the Canvas instance stored in app state.
    Works with both HTTP requests and WebSockets.
    """
    canvas = connection.app.state.canvas

    # Initialize Redis client if not already done
    if not canvas.redis_client:
        redis_client = get_redis(connection)

        # Initialize canvas data from Redis
        if redis_client:
            try:
                canvas.initialize_from_redis(redis_client)
            except Exception as e:
                print(f"Error initializing canvas from Redis: {e}", flush=True)

    return canvas


async def get_ws_manager(connection: HTTPConnection):
    """
    Get the WebSocketManager instance stored in app state.
    Works with both HTTP requests and WebSockets.
    """
    return connection.app.state.ws_manager


def get_redis(connection: HTTPConnection):
    """Dependency to provide Redis client stored in app state,"""
    redis_client = connection.app.state.redis_client
    try:
        # Ping Redis to make sure the connection is alive
        redis_client.ping()
        print("Successfully connected to Redis", flush=True)
        return redis_client
    except redis.exceptions.ConnectionError as e:
        print(f"Warning: Redis connection failed: {e}", flush=True)
        # Return None to indicate connection failure
        return None
