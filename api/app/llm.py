from app.config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key


def get_llm_client(settings: Settings) -> LLMClient:
    return LLMClient(settings=settings)
