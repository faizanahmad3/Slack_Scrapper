import logging
from typing import Dict

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import Settings
from app.providers.base import EmbeddingsProvider, LLMProvider
from app.providers.openai_embeddings import OpenAIEmbeddingsProvider
from app.providers.openai_llm import OpenAIChatProvider

logger = logging.getLogger(__name__)


EMBEDDING_PROVIDERS: Dict[str, EmbeddingsProvider] = {
    "openai": OpenAIEmbeddingsProvider(),
}

LLM_PROVIDERS: Dict[str, LLMProvider] = {
    "openai": OpenAIChatProvider(),
}


def get_embeddings(settings: Settings) -> Embeddings:
    provider_name = settings.embedding_provider.lower()
    logger.info(f"Creating embeddings provider: {provider_name}, model: {settings.embedding_model}")
    if provider_name not in EMBEDDING_PROVIDERS:
        logger.error(f"Unknown embedding provider: {provider_name}")
        raise ValueError(f"Unknown embedding provider: {provider_name}")
    embeddings = EMBEDDING_PROVIDERS[provider_name].create(settings)
    logger.info(f"Successfully created embeddings provider: {provider_name}")
    return embeddings


def get_llm(settings: Settings) -> BaseChatModel:
    provider_name = settings.llm_provider.lower()
    logger.info(f"Creating LLM provider: {provider_name}, model: {settings.llm_model}")
    if provider_name not in LLM_PROVIDERS:
        logger.error(f"Unknown LLM provider: {provider_name}")
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    llm = LLM_PROVIDERS[provider_name].create(settings)
    logger.info(f"Successfully created LLM provider: {provider_name}")
    return llm
