from app.providers.base import LLMProvider


class MockProvider(LLMProvider):
    def analyze_match(
        self, resume_text: str, role_description_text: str
    ) -> dict:
        return {
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
