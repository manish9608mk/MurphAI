from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# MurphAI Application Settings


class Settings(BaseSettings):
    """
    Runtime configuration for the MurphAI API.

    Values are loaded from environment variables and, for local
    development, from the .env file. Secrets should never be
    stored directly in source code.
    """

    # Human-readable application name used by the API metadata
    # and health/readiness responses.
    app_name: str = "MurphAI"

    # Application version used by the API metadata.
    app_version: str = "0.1.0"

    # Deployment environment.
    #
    # This currently documents the runtime environment and is
    # intentionally not used to change application behavior.
    environment: str = "development"

    # JWT signing secret.
    #
    # A minimum length of 32 characters helps prevent accidentally
    # using weak secrets for token signing.
    secret_key: str = Field(min_length=32)

    # JWT signing algorithm.
    #
    # Restricting this value prevents accidental configuration
    # changes to an unsupported or unexpected algorithm.
    algorithm: Literal["HS256"] = "HS256"

    # PostgreSQL connection string used by the backend.
    database_url: str

    # Browser origins allowed to call the API.
    #
    # Multiple origins can be provided as a comma-separated value.
    # Keeping the default empty prevents accidental cross-origin
    # access when CORS has not been explicitly configured.
    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """
        Convert the comma-separated CORS configuration into
        a clean list of browser origins.
        """

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()