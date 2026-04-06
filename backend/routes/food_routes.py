from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from backend.schemas.food import PredictFoodResponse
from backend.services.food_analysis_service import FoodAnalysisService

router = APIRouter()

_analysis_service = FoodAnalysisService()


@router.post("/predict_food", response_model=PredictFoodResponse)
async def predict_food(
    file: Optional[UploadFile] = File(None),
    food_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
) -> PredictFoodResponse:

    # Validation
    if not file and not food_name:
        raise HTTPException(status_code=400, detail="Provide image or food_name")

    try:
        content: Optional[bytes] = None

        # Read image if provided
        if file and file.filename:
            content = await file.read()

        # Call service
        result = await _analysis_service.analyze(
            user_id=user_id or "guest",
            image_bytes=content,
            food_name=food_name
        )

        return PredictFoodResponse(
            food_name=result.food_name,
            detected_from_image=result.detected_from_image,
            mapped_food_name=result.mapped_food_name,
            model_confidence=result.model_confidence,
            nutrients=result.nutrients,
            disease_suitability=result.disease_flags,
            diet_type=result.diet_type,
            recommendation_notes=result.recommendation_notes,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food analysis failed: {str(e)}")
