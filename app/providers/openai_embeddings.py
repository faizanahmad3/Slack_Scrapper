from langchain_openai import OpenAIEmbeddings

from app.config import Settings
from app.providers.base import EmbeddingsProvider


class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    def create(self, settings: Settings) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
