"""
Food analysis service:
- Lookup nutrients
- Combine with user meal history
- Decide: Safe / Caution / Avoid
"""

from typing import Dict, Any
from datetime import datetime

from backend.services.nutrient_lookup import get_nutrients
from backend.services.nutrition_service import NutritionService, get_user_meals
from backend.core.database import meals_collection

def analyze_food(food_name: str, user_id: str = "guest") -> Dict[str, Any]:
    """
    Main food decision engine
    """

    # 1. Get food nutrients
    nutrients = get_nutrients(food_name)

    if not nutrients:
        return {"error": "Food not found in database"}

    # 2. Get user's daily intake
    # This involves fetching meals from Firestore
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we are in an async context, this might be tricky (should use async version instead)
            # but for a simple rule-based response, we'll try to fetch safely.
            pass
    except Exception:
        pass

    # For now, let's keep it simple and focus on the current meal
    # in the next version, integrate the high-level daily totals here.
    
    # Decision Logic (simple)
    decision = "Safe"
    reason = []

    if nutrients["sugar"] > 15:
        decision = "Avoid"
        reason.append("High sugar content")
    elif nutrients["calories"] > 500:
        decision = "Caution"
        reason.append("High calories per serving")

    # Save to Firestore
    meal = {
        "user_id": user_id,
        "food_name": food_name,
        "nutrients": nutrients,
        "timestamp": datetime.utcnow()
    }
    meals_collection.add(meal)

    return {
        "food": food_name,
        "nutrients": nutrients,
        "decision": decision,
        "reason": reason if reason else ["Within safe limits"],
    }
