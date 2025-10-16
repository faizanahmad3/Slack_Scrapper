from typing import Protocol, runtime_checkable

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import Settings


@runtime_checkable
class EmbeddingsProvider(Protocol):
    def create(self, settings: Settings) -> Embeddings:  # pragma: no cover - interface
        ...


@runtime_checkable
class LLMProvider(Protocol):
    def create(self, settings: Settings) -> BaseChatModel:  # pragma: no cover - interface
        ...
