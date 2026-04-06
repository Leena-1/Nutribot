from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime

from backend.core.database import meals_collection
from backend.services.nutrient_lookup import get_nutrients
from backend.utils.errors import NotFoundError


class NutritionService:
    def lookup(self, name: str) -> Dict[str, Any]:
        nutrients = get_nutrients(name)

        if not nutrients:
            raise NotFoundError("Food not found.", details={"query": name})

        return {
            "food_name": name,
            "calories": nutrients.get("calories", 0),
            "protein": nutrients.get("protein", 0),
            "fat": nutrients.get("fat", 0),
            "carbs": nutrients.get("carbohydrates", 0),
            "sugar": nutrients.get("sugar", 0),
            "sodium": nutrients.get("sodium", 0),
        }

    def disease_flags(self, nutrients: Dict[str, Any]) -> Dict[str, int]:
        flags = {
            "suitable_diabetes": 1,
            "suitable_blood_pressure": 1,
            "suitable_heart": 1,
        }

        if nutrients["sugar"] > 25:
            flags["suitable_diabetes"] = 0

        if nutrients["sodium"] > 500:
            flags["suitable_blood_pressure"] = 0

        if nutrients["fat"] > 30:
            flags["suitable_heart"] = 0

        return flags


async def get_user_meals(user_id: str) -> List[Dict[str, Any]]:
    """
    Fetch user's meals history from Firestore using stream().
    """
    meals_query = meals_collection.where("user_id", "==", user_id).order_by("timestamp").stream()
    
    return [m.to_dict() for m in meals_query]


from backend.core.database import meals_collection, users_collection

async def analyze_user_query(user_id: str, food_name: str) -> Dict[str, Any]:
    """
    Main entry for food decision and storage (Firestore).
    """
    service = NutritionService()

    # 🔍 Step 1: Get nutrients
    nutrients = service.lookup(food_name)

    # 🧠 Step 2: Disease check
    flags = service.disease_flags(nutrients)

    # 💾 Step 3: Store in Firestore
    meal = {
        "user_id": user_id,
        "food_name": food_name,
        "nutrients": nutrients,
        "timestamp": datetime.utcnow()
    }
    meals_collection.add(meal)

    # 📊 Step 4: Calculate total daily intake (Firestore history)
    all_meals = await get_user_meals(user_id)
    
    # Filter for today only (UTC)
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    daily_meals = [m for m in all_meals if m.get("timestamp").replace(tzinfo=None) >= today_start]

    total = {"calories": 0, "sugar": 0, "sodium": 0, "protein": 0, "fat": 0, "carbs": 0}
    for m in daily_meals:
        n = m.get("nutrients", {})
        total["calories"] += n.get("calories", 0)
        total["sugar"] += n.get("sugar", 0)
        total["sodium"] += n.get("sodium", 0)
        total["protein"] += n.get("protein", 0)
        total["fat"] += n.get("fat", 0)
        total["carbs"] += n.get("carbs", 0)

    # ⚖️ Step 5: Decision logic + Detailed Reasoning
    decision = "Eat"
    reason = "This food fits well within your daily nutritional goals."
    
    # Fetch user profile for context
    user_doc = users_collection.document(user_id).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    diseases = [d.lower() for d in user_data.get("diseases", [])]
    calorie_limit = user_data.get("calorie_limit", 2000)

    # Update Calorie Remaining in Firestore
    calorie_remaining = calorie_limit - total["calories"]
    users_collection.document(user_id).set({"calorie_remaining": calorie_remaining}, merge=True)

    # Decision logic
    if total["calories"] > calorie_limit:
        decision = "Avoid"
        reason = f"You've exceeded your daily calorie goal of {calorie_limit} kcal. Consider exercise to burn extra!"
    elif "diabetes" in diseases and total["sugar"] > 40:
        decision = "Avoid"
        reason = f"Your daily sugar intake ({round(total['sugar'], 1)}g) is high for your diabetes management plan."
    elif total["sodium"] > 2300:
        decision = "Avoid"
        reason = "Your sodium intake has exceeded the recommended daily limit of 2300mg."
    elif nutrients.get("sugar", 0) > 15 and "diabetes" in diseases:
        decision = "Caution"
        reason = "This food is high in sugar. Since you have diabetes, consider a smaller portion."

    return {
        "user_id": user_id,
        "food": food_name,
        "nutrients": nutrients,
        "disease_flags": flags,
        "daily_total": total,
        "decision": decision,
        "reason": reason,
        "calorie_remaining": calorie_remaining
    }
