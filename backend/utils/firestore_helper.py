from backend.core.database import users_collection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_user_profile(uid: str):
    """Fetch user profile from Firestore."""
    try:
        doc = users_collection.document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Error fetching user profile for {uid}: {e}")
        return None

async def update_daily_intake(uid: str, meal_data: dict):
    """
    Update daily intake in Firestore and recalculate remaining targets.
    meal_data should contain: calories, protein, carbs, fat, sugar, sodium, fiber
    """
    try:
        user_ref = users_collection.document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.error(f"User {uid} not found")
            return False
            
        user_data = user_doc.to_dict()
        
        # Current values (default to 0 if missing)
        cal_consumed = user_data.get("calories_consumed", 0) + meal_data.get("calories", 0)
        protein_consumed = user_data.get("protein_consumed", 0) + meal_data.get("protein", 0)
        carbs_consumed = user_data.get("carbs_consumed", 0) + meal_data.get("carbs", 0)
        fat_consumed = user_data.get("fat_consumed", 0) + meal_data.get("fat", 0)
        sugar_consumed = user_data.get("sugar_consumed", 0) + meal_data.get("sugar", 0)
        sodium_consumed = user_data.get("sodium_consumed", 0) + meal_data.get("sodium", 0)
        fiber_consumed = user_data.get("fiber_consumed", 0) + meal_data.get("fiber", 0)
        
        # Targets
        cal_target = user_data.get("calorie_target", 2000)
        fiber_target = user_data.get("fiber_target", 25)
        sodium_limit = user_data.get("sodium_limit", 2300)
        carb_limit = user_data.get("carb_limit", 300)
        
        # Calculate remaining
        cal_remaining = cal_target - cal_consumed
        fiber_remaining = max(0, fiber_target - fiber_consumed)
        sodium_remaining = max(0, sodium_limit - sodium_consumed)
        carb_remaining = max(0, carb_limit - carbs_consumed)
        
        # Update flat fields
        updates = {
            "calories_consumed": cal_consumed,
            "protein_consumed": protein_consumed,
            "carbs_consumed": carbs_consumed,
            "fat_consumed": fat_consumed,
            "sugar_consumed": sugar_consumed,
            "sodium_consumed": sodium_consumed,
            "fiber_consumed": fiber_consumed,
            "calorie_remaining": cal_remaining,
            "fiber_remaining": fiber_remaining,
            "sodium_remaining": sodium_remaining,
            "carb_remaining": carb_remaining
        }
        
        # Add to daily_meals list
        meal_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **meal_data
        }
        
        # Use ArrayUnion to add to the list
        from google.cloud import firestore
        updates["daily_meals"] = firestore.ArrayUnion([meal_entry])
        
        user_ref.update(updates)
        
        return True
    except Exception as e:
        logger.error(f"Error updating daily intake for {uid}: {e}")
        return False
