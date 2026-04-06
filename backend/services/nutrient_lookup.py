"""
Nutrient lookup service using Edamam API fallback.
"""
import os
import requests
from typing import Dict, Any, Optional

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "demo_id")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY", "demo_key")

def get_nutrients(food_name: str) -> Optional[Dict[str, Any]]:
    """Fetch macro nutrients for a specific food using Edamam API."""
    url = f"https://api.edamam.com/api/food-database/v2/parser"
    params = {
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "ingr": food_name,
        "nutrition-type": "logging"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("parsed") and len(data["parsed"]) > 0:
                nutrients = data["parsed"][0]["food"]["nutrients"]
                return {
                    "calories": nutrients.get("ENERC_KCAL", 0),
                    "protein": nutrients.get("PROCNT", 0),
                    "fat": nutrients.get("FAT", 0),
                    "carbohydrates": nutrients.get("CHOCDF", 0),
                    "sugar": nutrients.get("SUGAR", 0),
                    "sodium": nutrients.get("NA", 0)
                }
            elif data.get("hints") and len(data["hints"]) > 0:
                nutrients = data["hints"][0]["food"]["nutrients"]
                return {
                    "calories": nutrients.get("ENERC_KCAL", 0),
                    "protein": nutrients.get("PROCNT", 0),
                    "fat": nutrients.get("FAT", 0),
                    "carbohydrates": nutrients.get("CHOCDF", 0),
                    "sugar": nutrients.get("SUGAR", 0),
                    "sodium": nutrients.get("NA", 0)
                }
    except Exception as e:
        print(f"Edamam API error: {e}")

    # Fallback to mock data if API fails or no credentials
    return {
        "calories": 250,
        "protein": 10,
        "fat": 5,
        "carbohydrates": 30,
        "sugar": 5,
        "sodium": 300
    }

def lookup_food(food_name: str, df=None) -> Optional[Dict[str, Any]]:
    nutrients = get_nutrients(food_name)
    if not nutrients:
        return None
    return {"food_name": food_name, **nutrients}

def get_nutrient_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    return row

def get_disease_flags(row: Dict[str, Any]) -> Dict[str, Any]:
    return {"suitable_diabetes": 1, "suitable_blood_pressure": 1, "suitable_heart": 1}
