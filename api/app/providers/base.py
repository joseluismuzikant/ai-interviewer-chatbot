from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def analyze_match(
        self, resume_text: str, role_description_text: str
    ) -> dict:
        ...
