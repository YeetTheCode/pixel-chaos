from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings with environment variable names
    mongodb_url: str = (
        "mongodb://root:example@mongo:27017/"  # Default without credentials
    )
    db_name: str = "pixel_chaos"
    redis_url: str = "redis://redis:6379"

    # Add model_config to specify env file and env name mapping
    class Config:
        env_file = ".env"
        # This explicitly maps environment variables to fields
        env_prefix = ""  # No prefix for environment variables


settings = Settings()
