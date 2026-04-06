from typing import Optional, List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str
    intent_hint: Optional[str] = None

class FoodResult(BaseModel):
    food_item: str
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    cholesterol_mg: float
    gi_index: Optional[float]
    meal_type: str
    health_tags: str
    veg_nonveg: str
    did_you_mean: bool = False
    disease_warning: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    intent: str
    foods: Optional[List[FoodResult]] = None
    needs_exercise: bool = False
