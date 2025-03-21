from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings with environment variable names
    mongodb_url: str = (
        "mongodb://root:example@mongo:27017/"  # Default without credentials
    )
    db_name: str = "pixel_chaos"
    redis_url: str = "redis://redis:6379"

    # Configure Redis connection
    redis_host: str = "redis-stack"  # Match the service name in docker-compose.yml
    redis_port: int = 6379  # Default Redis port
    redis_decode_responses: bool = (
        True  # Automatically decode byte responses to strings
    )
    redis_socket_timeout: int = 5  # Add timeout to avoid hanging
    redis_socket_connect_timeout: int = 5

    # Add model_config to specify env file and env name mapping
    class Config:
        env_file = ".env"
        # This explicitly maps environment variables to fields
        env_prefix = ""  # No prefix for environment variables


settings = Settings()
