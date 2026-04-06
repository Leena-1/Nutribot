from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from .auth_routes import router as auth_router
from .food_router import router as food_router
from .exercise_router import router as exercise_router
from .chat_router import router as chat_router
from .safety_router import router as safety_router

from backend.schemas.food import PredictFoodResponse
from backend.services.food_analysis_service import FoodAnalysisService

# Main API Router
router = APIRouter()

# Register routers
router.include_router(auth_router, tags=["Authentication"])
router.include_router(food_router, prefix="/food", tags=["Food Management"])
router.include_router(exercise_router, prefix="/exercise", tags=["Exercise Management"])
router.include_router(chat_router, prefix="/chat", tags=["AI Chat"])
router.include_router(safety_router, prefix="/safety", tags=["Food Safety"])

# Global Service Instances
_analysis_service = FoodAnalysisService()

# -----------------------------
# ROOT / HEALTH within /api
# -----------------------------
@router.get("/health")
async def api_health():
    return {"status": "ok", "version": "1.0.0"}
