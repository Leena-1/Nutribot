from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NutrientSummary(BaseModel):
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    total_fat_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugars_g: Optional[float] = None
    sodium_mg: Optional[float] = None

    potassium_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    vitamin_a_iu: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    saturated_fat_g: Optional[float] = None

    # Engineered features
    calorie_density: Optional[float] = Field(default=None, description="kcal per gram (assuming nutrients are per 100g)")
    sugar_ratio: Optional[float] = Field(default=None, description="sugars_g / carbohydrates_g")
    fat_ratio: Optional[float] = Field(default=None, description="total_fat_g / (protein_g + carbohydrates_g + total_fat_g)")
    sodium_ratio: Optional[float] = Field(default=None, description="sodium_mg / energy_kcal")


class DiseaseRisk(BaseModel):
    probability: float = Field(ge=0.0, le=1.0)
    label: int = Field(description="0=low risk, 1=high risk (model-dependent threshold)")
    top_factors: Dict[str, float] = Field(default_factory=dict, description="feature_name -> contribution proxy")


class DiseaseSuitability(BaseModel):
    suitable_diabetes: int = Field(default=-1, description="1 suitable, 0 not suitable, -1 unknown")
    suitable_blood_pressure: int = Field(default=-1)
    suitable_heart: int = Field(default=-1)

    # Optional probability outputs
    diabetes_risk: Optional[DiseaseRisk] = None
    blood_pressure_risk: Optional[DiseaseRisk] = None
    heart_risk: Optional[DiseaseRisk] = None


class PredictFoodResponse(BaseModel):
    food_name: Optional[str] = None
    detected_from_image: bool = False
    mapped_food_name: Optional[str] = Field(default=None, description="Nutrition dataset key after mapping")
    model_confidence: Optional[float] = None

    nutrients: NutrientSummary = Field(default_factory=NutrientSummary)
    disease_suitability: DiseaseSuitability = Field(default_factory=DiseaseSuitability)

    diet_type: Optional[str] = None
    recommendation_notes: Optional[str] = None
    user_id: Optional[str] = None

    # Backwards-compatible message field (Flutter shows this when present)
    message: Optional[str] = None

