from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

# Proactively load .env from the nearest path to the current working dir
load_dotenv(find_dotenv(usecwd=True), override=False)


class Settings(BaseSettings):
    # Provider selection
    embedding_provider: str = Field(default="openai", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_temperature: Optional[str] = Field(default=None, alias="OPENAI_TEMPERATURE")
    slack_bot_token: Optional[str] = Field(default=None, alias="SLACK_BOT_TOKEN")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost", alias="QDRANT_URL")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")

    # Ingestion limits
    max_messages_per_channel: Optional[int] = Field(default=None, alias="MAX_MESSAGES_PER_CHANNEL")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
