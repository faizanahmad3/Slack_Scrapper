from langchain_openai import ChatOpenAI

from app.config import Settings
from app.providers.base import LLMProvider


class OpenAIChatProvider(LLMProvider):
    def create(self, settings: Settings) -> ChatOpenAI:
        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
        )