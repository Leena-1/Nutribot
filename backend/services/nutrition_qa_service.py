from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from backend.services.food_analysis_service import FoodAnalysisService
from backend.utils.errors import NotFoundError


_COND_PATTERNS = [
    ("diabetes", re.compile(r"\b(diabetes|diabetic|blood sugar|glucose)\b", re.I)),
    ("blood_pressure", re.compile(r"\b(blood pressure|hypertension|bp)\b", re.I)),
    ("heart", re.compile(r"\b(heart|cholesterol|cardio)\b", re.I)),
]

_FOOD_CAPTURE = re.compile(
    r"(?:can|should|is|are)\s+(?:a\s+)?(?:diabetics?|people|someone|patients?)?.*?"
    r"(?:eat|have|drink|consume|avoid|bad|good)\s+(?P<food>[a-zA-Z][a-zA-Z\s\-']{2,})\??$",
    re.I,
)


@dataclass(frozen=True)
class QAResult:
    handled: bool
    response: str


class NutritionQAService:
    """
    Retrieval-based Q&A over the nutrition database + disease risk model.
    """

    def __init__(self):
        self._analysis = FoodAnalysisService()

    async def answer(self, query: str) -> QAResult:
        q = (query or "").strip()
        if not q:
            return QAResult(False, "")

        condition: Optional[str] = None
        for name, pat in _COND_PATTERNS:
            if pat.search(q):
                condition = name
                break

        m = _FOOD_CAPTURE.search(q)
        if not condition or not m:
            return QAResult(False, "")

        food = " ".join(m.group("food").strip().split())
        try:
            r = await self._analysis.analyze(food_name=food)
        except NotFoundError:
            return QAResult(True, f"I couldn't find “{food}” in the nutrition database. Try a more specific name.")
        except Exception:
            return QAResult(False, "")

        nutrients = r.nutrients or {}
        flags = r.disease_flags or {}

        if condition == "diabetes":
            suit = flags.get("suitable_diabetes", -1)
            risk = (flags.get("diabetes_risk") or {})
            key_nutr = f"sugar={nutrients.get('sugars_g', 'n/a')}g, carbs={nutrients.get('carbohydrates_g', 'n/a')}g"
        elif condition == "blood_pressure":
            suit = flags.get("suitable_blood_pressure", -1)
            risk = (flags.get("blood_pressure_risk") or {})
            key_nutr = f"sodium={nutrients.get('sodium_mg', 'n/a')}mg"
        else:
            suit = flags.get("suitable_heart", -1)
            risk = (flags.get("heart_risk") or {})
            key_nutr = f"sat_fat={nutrients.get('saturated_fat_g', 'n/a')}g, cholesterol={nutrients.get('cholesterol_mg', 'n/a')}mg"

        prob = risk.get("probability")
        prob_txt = f" (risk≈{prob:.0%})" if isinstance(prob, (int, float)) else ""

        if suit == 1:
            verdict = "Generally yes"
        elif suit == 0:
            verdict = "Usually not recommended"
        else:
            verdict = "It depends"

        tip = {
            "diabetes": "Keep portions moderate and pair with fiber/protein to blunt glucose spikes.",
            "blood_pressure": "Prefer low-sodium preparation; avoid processed/high-salt versions.",
            "heart": "Limit saturated fat; choose baked/grilled options and add fiber-rich sides.",
        }[condition]

        return QAResult(
            True,
            f"{verdict}{prob_txt} for {condition.replace('_', ' ')}. For “{r.food_name}”: {key_nutr}. {tip}",
        )

