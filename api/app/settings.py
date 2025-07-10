import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "mushare"

    LINK_CACHE_TTL_SECONDS: int = 3600 * 24 * 30 # 30 days

    # Spotify Web API deets
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")

    # Apple Music API deets
    APPLE_MUSIC_TEAM_ID: str = os.getenv("APPLE_MUSIC_TEAM_ID", "")
    APPLE_MUSIC_KEY_ID: str = os.getenv("APPLE_MUSIC_KEY_ID", "")
    APPLE_MUSIC_PRIVATE_KEY_PATH: str = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH", "mushare.p8")

    # PostHog deets
    POSTHOG_API_KEY: str = os.getenv("POSTHOG_API_KEY", "")
    POSTHOG_HOST: str = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")

    class Config:
        case_sensitive = True

settings = Settings() 