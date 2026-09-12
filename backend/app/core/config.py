from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# MurphAI Application Settings

class Settings(BaseSettings):
    app_name: str = "MurphAI"
    app_version: str = "0.1.0"
    environment: str = "development"

    # JWT security configuration.
    # A short secret makes token signing easier to attack.
    secret_key: str = Field(min_length=32)

    # Keep the JWT algorithm explicit and predictable.
    algorithm: Literal["HS256"] = "HS256"

    database_url: str

    # Comma-separated browser origins allowed to access the API.
    # Empty by default so the API does not accidentally allow
    # arbitrary browser origins.
    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
