from app.config import Settings
from app.providers.base import LLMProvider
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock import MockProvider
from app.providers.openai_provider import OpenAIProvider

_PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "mock": MockProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
}


def get_llm_client(settings: Settings) -> LLMProvider:
    provider_name = settings.llm_provider.lower().strip()

    if provider_name not in _PROVIDER_MAP:
        valid = ", ".join(_PROVIDER_MAP)
        raise ValueError(
            f"Unknown LLM_PROVIDER '{settings.llm_provider}'. "
            f"Valid options: {valid}"
        )

    provider_class = _PROVIDER_MAP[provider_name]

    if provider_name == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Configure it in .env to use the OpenAI provider."
            )
    elif provider_name == "gemini":
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set. Configure it in .env to use the Gemini provider."
            )
    elif provider_name == "deepseek":
        if not settings.deepseek_api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is not set. Configure it in .env to use the DeepSeek provider."
            )

    return provider_class(settings=settings)
