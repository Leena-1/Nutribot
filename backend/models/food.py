from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class FoodPrediction:
    class_name: str
    confidence: float


@dataclass(frozen=True)
class FoodAnalysisResult:
    food_name: str
    detected_from_image: bool
    mapped_food_name: str
    model_confidence: Optional[float]
    nutrients: Dict[str, Any]
    disease_flags: Dict[str, Any]
    diet_type: Optional[str]
    recommendation_notes: Optional[str]

