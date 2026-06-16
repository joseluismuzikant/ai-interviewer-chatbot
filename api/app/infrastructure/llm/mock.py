from app.domain.interfaces.llm_provider import LLMProvider
from app.schemas import (
    AnswerEvaluation,
    GeneratedReport,
    InterviewQuestion,
    MatchAnalysis,
)


class MockProvider(LLMProvider):
    def __init__(self, settings=None) -> None:
        pass

    def analyze_match(
        self, resume_text: str, role_description_text: str
    ) -> dict:
        analysis = {
            "role_summary": (
                "The role requires a Senior Full-Stack Engineer proficient in "
                "Python, TypeScript, React, FastAPI, and cloud infrastructure."
            ),
            "candidate_summary": (
                "The candidate is an experienced engineer with a strong "
                "background in Python, TypeScript, React, and FastAPI. Cloud "
                "experience is present but limited compared to role expectations."
            ),
            "focus_areas": [
                {
                    "topic": "Python and FastAPI",
                    "reason": (
                        "Core requirement of the role and a demonstrated "
                        "strength of the candidate."
                    ),
                },
                {
                    "topic": "React and TypeScript",
                    "reason": (
                        "Frontend stack used by the team; the candidate has "
                        "relevant hands-on experience."
                    ),
                },
            ],
            "potential_gaps": [
                {
                    "topic": "Cloud Infrastructure",
                    "reason": (
                        "The role expects deep cloud expertise, but the "
                        "candidate only has foundational exposure."
                    ),
                },
            ],
        }
        return MatchAnalysis.model_validate(analysis).model_dump()

    def generate_question(self, context: dict) -> dict:
        question_number = int(context.get("question_number", 1))
        question = {
            "question": (
                "Can you describe how you would design a scalable REST API "
                "for a financial services application?"
                if question_number == 1
                else "How would you improve that API's reliability and observability under production load?"
            ),
            "topic": "Backend API design" if question_number == 1 else "Reliability and observability",
            "difficulty": 5,
            "expected_signals": [
                "API resource design" if question_number == 1 else "SLO and metrics definition",
                "validation and error handling",
                "security considerations" if question_number == 1 else "failure-mode planning",
                "database transaction boundaries" if question_number == 1 else "alerting strategy",
                "observability",
            ],
        }
        return InterviewQuestion.model_validate(question).model_dump()

    def evaluate_answer(self, context: dict) -> dict:
        evaluation = {
            "score": 7,
            "rationale": "The answer demonstrates a solid understanding of the topic with enough technical detail for the MVP.",
            "evidence": "The candidate describes API design, validation, and scalability considerations.",
            "followup_hint": "Ask the candidate to go deeper into error handling, observability, and production trade-offs.",
        }
        return AnswerEvaluation.model_validate(evaluation).model_dump()

    def generate_report(self, context: dict) -> dict:
        report = {
            "summary": "The candidate demonstrated solid full-stack engineering experience with good backend and cloud understanding.",
            "strengths": [
                "Strong backend and API design knowledge",
                "Good experience with cloud-native delivery",
                "Clear practical examples from previous projects",
            ],
            "weaknesses": [
                "Could provide more depth on security and authorization",
                "Could explain database trade-offs in more detail",
            ],
            "recommendation": "YES",
            "recommendation_rationale": "The candidate shows enough technical strength and relevant experience for the role.",
        }
        return GeneratedReport.model_validate(report).model_dump()
