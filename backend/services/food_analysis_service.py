from __future__ import annotations
import asyncio
from typing import Optional
from datetime import datetime

from backend.core.database import meals_collection
from backend.models.food import FoodAnalysisResult, FoodPrediction
from backend.services.food_model_service import FoodClassifierService, FoodMapping
from backend.services.cache_provider import get_cache
from backend.services.image_processor import preprocess_image
from backend.services.nutrition_service import NutritionService, get_user_meals
from backend.utils.errors import NotFoundError


class FoodAnalysisService:
    def __init__(
        self,
        *,
        classifier: Optional[FoodClassifierService] = None,
        mapping: Optional[FoodMapping] = None,
        nutrition: Optional[NutritionService] = None,
    ):
        self._classifier = classifier or FoodClassifierService()
        self._mapping = mapping or FoodMapping()
        self._nutrition = nutrition or NutritionService()

    async def analyze(
        self,
        *,
        user_id: str,
        image_bytes: Optional[bytes] = None,
        food_name: Optional[str] = None,
    ) -> FoodAnalysisResult:

        cache = get_cache()

        # ================= CACHE =================
        if not image_bytes and food_name:
            key = "analysis:name:" + " ".join(food_name.lower().strip().split())
            cached = await cache.get(key)
            if isinstance(cached, dict) and cached.get("food_name"):
                return FoodAnalysisResult(**cached)

        detected: Optional[FoodPrediction] = None

        # ================= IMAGE PROCESS =================
        if image_bytes:
            loop = asyncio.get_event_loop()
            optimized_image = await loop.run_in_executor(None, preprocess_image, image_bytes)
            detected = await self._classifier.predict(optimized_image)

        raw_name = (detected.class_name if detected else (food_name or "")).strip()

        if not raw_name:
            raise NotFoundError("Provide image or food_name")

        mapped = (
            self._mapping.map_to_nutrition_name(raw_name)
            if detected
            else raw_name.lower()
        )

        # ================= NUTRITION =================
        nutrients = self._nutrition.lookup(mapped)
        disease_flags = self._nutrition.disease_flags(nutrients)

        # ================= STORE MEAL (FIRESTORE) =================
        meal = {
            "user_id": user_id,
            "food_name": mapped,
            "nutrients": nutrients,
            "timestamp": datetime.utcnow(),
        }

        # Store in Firestore
        meals_collection.add(meal)

        # ================= DAILY TOTAL (FIRESTORE) =================
        from backend.services.nutrition_service import analyze_user_query
        
        # Use our updated central analysis function to get consistent reasoning/totals
        # This will also store the meal in Firestore
        analysis = await analyze_user_query(user_id, mapped)
        
        total = analysis["daily_total"]
        decision = analysis["decision"]
        reason = analysis["reason"]
        cal_rem = analysis["calorie_remaining"]

        # ================= EXERCISE RECOMENDATION IF NEEDED =================
        exercise_note = ""
        if cal_rem <= 0:
            from backend.services.exercise_service import exercise_service
            from backend.core.database import users_collection
            
            user_doc = users_collection.document(user_id).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            exercises = exercise_service.recommend_exercises(
                bmi_group=user_data.get("bmi_group", "Normal"),
                activity_level=user_data.get("activity_level", "Sedentary"),
                medical_condition=user_data.get("medical_condition", "None")
            )
            if exercises:
                exercise_note = "\n\n🔥 Limit reached! Recommended exercises:\n"
                for i, ex in enumerate(exercises[:3], 1):
                    exercise_note += f"{i}. {ex['name']} ({ex['duration']}m) -> ~{int(ex['calories_burned'])}kcal\n"

        # ================= RESULT =================
        result = FoodAnalysisResult(
            food_name=mapped,
            detected_from_image=bool(detected),
            mapped_food_name=mapped,
            model_confidence=(float(detected.confidence) if detected else None),
            nutrients=nutrients,
            disease_flags=disease_flags,
            diet_type=None,
            recommendation_notes=f"Decision: {decision}\nReason: {reason}{exercise_note}",
        )

        # ================= CACHE STORE =================
        if not image_bytes and food_name:
            await cache.set(
                "analysis:name:" + " ".join(food_name.lower().strip().split()),
                {
                    "food_name": result.food_name,
                    "detected_from_image": result.detected_from_image,
                    "mapped_food_name": result.mapped_food_name,
                    "model_confidence": result.model_confidence,
                    "nutrients": result.nutrients,
                    "disease_flags": result.disease_flags,
                    "diet_type": result.diet_type,
                    "recommendation_notes": result.recommendation_notes,
                },
            )

        return result

    # ================= TEXT ENTRY SUPPORT =================
    async def analyze_text(self, user_id: str, food_name: str):
        return await self.analyze(user_id=user_id, food_name=food_name)
