# src/services/explainability.py
"""Generate recruiter-friendly explanations - unbiased, concise, and consistent."""
from __future__ import annotations

import re
from src.services.gemini_client import GeminiClient


def _clean_text(s: str, max_chars: int) -> str:
    """Post-clean LLM output: remove markdown, normalize whitespace, cap length."""
    if not s:
        return ""

    # remove code fences / markdown bullets
    s = re.sub(r"```.*?```", "", s, flags=re.DOTALL)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"^\s*[-•]+\s*", "", s, flags=re.MULTILINE)

    # normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()

    # cap length safely
    if len(s) > max_chars:
        s = s[: max_chars - 1].rstrip() + "…"
    return s


def _two_sentence_cap(s: str, max_chars: int = 280) -> str:
    """
    Keep at most two sentences.
    If the model returns one long sentence, keep it but cap chars.
    """
    s = _clean_text(s, max_chars=max_chars)
    if not s:
        return s

    # Split into sentences roughly
    parts = re.split(r"(?<=[.!?])\s+", s)
    if len(parts) <= 2:
        return _clean_text(s, max_chars=max_chars)

    two = (parts[0] + " " + parts[1]).strip()
    return _clean_text(two, max_chars=max_chars)


class ExplainabilityGenerator:
    def __init__(self):
        # Keep text-mode GeminiClient; no JSON mode needed
        self.gemini = GeminiClient(debug=False)

    async def generate_explanation(self, job, candidate, match_result) -> str:
        """
        Generate a short recruiter note:
        - EXACTLY 3 sentences
        - <= 380 characters
        - mentions 2-3 strengths + 1 gap + next-step suggestion
        """
        status = match_result.get("evaluationStatus")
        score = match_result.get("matchScore")
        recommendation = match_result.get("recommendation", "Manual review")
        strengths = match_result.get("strengths", []) or []
        gaps = match_result.get("gaps", []) or []
        reasoning = match_result.get("reasoning", "") or ""

        # If evaluation failed, be transparent and fair.
        if status != "success" or score is None:
            err = match_result.get("error", "Gemini evaluation failed")
            msg = (
                f"Automated evaluation was unavailable for this candidate due to a temporary AI service issue "
                f"({err}). Please re-run screening or complete a manual review using the same criteria."
            )
            return _two_sentence_cap(msg, max_chars=280)

        # Keep only the most useful items
        s1 = strengths[0] if len(strengths) > 0 else "Meets several core requirements"
        s2 = strengths[1] if len(strengths) > 1 else ""
        g1 = gaps[0] if len(gaps) > 0 else "Some skills/experience details are unclear"

        # Strong output shaping: exact format + strict limits
        prompt = f"""
You are writing a recruiter note. Be unbiased and evaluate only qualifications.

CONTEXT
Job title: {job.title}
Score: {score}/100
Recommendation: {recommendation}

Top strengths:
1) {s1}
2) {s2 if s2 else "N/A"}

Top gap:
- {g1}

Extra context (optional):
{reasoning}

OUTPUT RULES (MUST FOLLOW)
- Write EXACTLY 3 sentences total.
- Total length <= 380 characters.
- Mention 2-3 strengths, 1 gap, and a next-step (interview/follow-up task).
- No markdown, no bullet points, no emojis.
""".strip()

        raw = await self.gemini.generate_text_response(prompt)

        # enforce “two sentences max” even if Gemini ignores format
        return _two_sentence_cap(raw, max_chars=280)

    async def generate_full_evaluation_report(self, job, candidate, match_result) -> str:
        """
        Slightly longer report for hiring manager:
        - 4 short paragraphs max
        - Still bias-safe
        - Uses strengths/gaps already extracted
        """
        status = match_result.get("evaluationStatus")
        score = match_result.get("matchScore")
        recommendation = match_result.get("recommendation", "Manual review")
        strengths = match_result.get("strengths", []) or []
        gaps = match_result.get("gaps", []) or []

        if status != "success" or score is None:
            err = match_result.get("error", "Gemini evaluation failed")
            msg = (
                f"Automated evaluation could not be completed due to a temporary AI service issue ({err}).\n\n"
                f"Recommended next step: re-run screening for this candidate, or proceed with a structured manual review "
                f"against required skills ({', '.join(job.requiredSkills)})."
            )
            return _clean_text(msg, max_chars=900)

        # Provide structured, consistent report format
        prompt = f"""
You are writing a hiring-manager evaluation summary. Be unbiased and focus only on job-relevant qualifications.

Job: {job.title}
Required skills: {", ".join(job.requiredSkills)}
Preferred skills: {", ".join(job.preferredSkills)}
Score: {score}/100
Recommendation: {recommendation}

Strengths: {", ".join(strengths[:3]) if strengths else "N/A"}
Gaps: {", ".join(gaps[:3]) if gaps else "N/A"}

OUTPUT FORMAT (MUST FOLLOW)
Paragraph 1 (1 sentence): Overall fit + score.
Paragraph 2 (1-2 sentences): Strongest evidence (skills/experience).
Paragraph 3 (1 sentence): Key gap/risk.
Paragraph 4 (1 sentence): Next step recommendation.

No markdown, no emojis. Keep total length <= 900 characters.
""".strip()

        raw = await self.gemini.generate_text_response(prompt)
        return _clean_text(raw, max_chars=900)