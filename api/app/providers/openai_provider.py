import json

from openai import OpenAI
from pydantic import ValidationError

from app.config import Settings
from app.providers.base import LLMProvider
from app.schemas import MatchAnalysis


class OpenAIProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if not self._client:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def analyze_match(
        self, resume_text: str, role_description_text: str
    ) -> dict:
        system_prompt = (
            "You are a hiring analyst. Given a resume and a role description, "
            "provide a structured analysis of the candidate-role match."
        )
        user_prompt = (
            f"Resume:\n{resume_text}\n\n"
            f"Role Description:\n{role_description_text}\n\n"
            "Return ONLY valid JSON with this exact structure, no explanation:\n"
            '{"role_summary": "string", "candidate_summary": "string", '
            '"focus_areas": [{"topic": "string", "reason": "string"}], '
            '"potential_gaps": [{"topic": "string", "reason": "string"}]}'
        )

        try:
            response = self._get_client().chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"OpenAI API call failed: {exc}"
            ) from exc

        content = response.choices[0].message.content or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid match analysis JSON.") from exc

        try:
            validated = MatchAnalysis.model_validate(result)
        except ValidationError as exc:
            raise RuntimeError("LLM returned invalid match analysis JSON.") from exc

        return validated.model_dump()
