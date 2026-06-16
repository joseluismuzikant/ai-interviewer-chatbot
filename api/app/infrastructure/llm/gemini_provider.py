import json

import google.generativeai as genai
from pydantic import ValidationError

from app.core.config import Settings
from app.domain.interfaces.llm_provider import LLMProvider
from app.schemas import AnswerEvaluation, GeneratedReport, InterviewQuestion, MatchAnalysis


class GeminiProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.model = settings.google_model
        self.api_key = settings.google_api_key

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set. Configure it in .env to use the Gemini provider."
            )

        genai.configure(api_key=self.api_key)

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
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
        except Exception as exc:
            raise RuntimeError(
                f"Gemini API call failed: {exc}"
            ) from exc

        content = response.text or "{}"
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

    def generate_question(self, context: dict) -> dict:
        system_prompt = (
            "You are an AI technical interviewer. Generate the first interview "
            "question from the provided focus areas and difficulty."
        )
        user_prompt = (
            f"Context JSON:\n{json.dumps(context)}\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            '{"question":"string","topic":"string","difficulty":5,'
            '"expected_signals":["string"]}'
        )

        try:
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        content = response.text or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid question JSON.") from exc

        try:
            validated = InterviewQuestion.model_validate(result)
        except ValidationError as exc:
            raise RuntimeError("LLM returned invalid question JSON.") from exc

        return validated.model_dump()

    def evaluate_answer(self, context: dict) -> dict:
        system_prompt = (
            "You are a technical interviewer evaluating a candidate answer. "
            "Provide strict JSON scoring output."
        )
        user_prompt = (
            f"Context JSON:\n{json.dumps(context)}\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            '{"score":7,"rationale":"string","evidence":"string","followup_hint":"string"}'
        )

        try:
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        content = response.text or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid answer evaluation JSON.") from exc

        try:
            validated = AnswerEvaluation.model_validate(result)
        except ValidationError as exc:
            raise RuntimeError("LLM returned invalid answer evaluation JSON.") from exc

        return validated.model_dump()

    def generate_report(self, context: dict) -> dict:
        system_prompt = (
            "You are a senior technical hiring panelist. Generate a concise final "
            "candidate report from the transcript and analysis context."
        )
        user_prompt = (
            f"Context JSON:\n{json.dumps(context)}\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            '{"summary":"string","strengths":["string"],"weaknesses":["string"],'
            '"recommendation":"YES | MIXED | NO","recommendation_rationale":"string"}'
        )

        try:
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        content = response.text or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid report JSON.") from exc

        try:
            validated = GeneratedReport.model_validate(result)
        except ValidationError as exc:
            raise RuntimeError("LLM returned invalid report JSON.") from exc

        return validated.model_dump()
