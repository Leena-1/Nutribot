"""
Preprocessing pipeline configuration.

Dataset paths and column mappings. Adjust these to match your actual
dataset file names and column headers.
"""

import os
from pathlib import Path

# Project root (parent of ml_model)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = PROJECT_ROOT / "datasets"
PROCESSED_DIR = DATASETS_DIR / "processed"

# Ensure processed output directory exists when pipeline runs
def ensure_processed_dir():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_config():
    """Return current config dict for reference or tests."""
    return {
        "project_root": str(PROJECT_ROOT),
        "datasets_dir": str(DATASETS_DIR),
        "processed_dir": str(PROCESSED_DIR),
        "paths": {
            "usda": get_usda_paths(),
            "meals": get_meals_paths(),
            "disease": get_disease_paths(),
            "diet_recommendation": get_diet_recommendation_paths(),
        },
        "usda_column_map": USDA_COLUMN_MAP,
        "meals_column_map": MEALS_COLUMN_MAP,
        "disease_column_map": DISEASE_COLUMN_MAP,
        "diet_column_map": DIET_COLUMN_MAP,
    }


# ---------------------------------------------------------------------------
# USDA FoodData Central
# ---------------------------------------------------------------------------
USDA_DIR = DATASETS_DIR / "usda"

def get_usda_paths():
    return {
        "dir": str(USDA_DIR),
        "food_file": str(USDA_DIR / "food.csv"),
        "food_nutrient_file": str(USDA_DIR / "food_nutrient.csv"),
        "nutrient_file": str(USDA_DIR / "nutrient.csv"),
        # Alternative: single merged CSV (if you have one)
        "single_food_nutrients_file": str(USDA_DIR / "food_nutrients.csv"),
    }

# Column names in USDA CSV files (SR Legacy / Foundation Foods style)
USDA_COLUMN_MAP = {
    "food": {
        "id": "fdc_id",
        "name": "description",
    },
    "food_nutrient": {
        "food_id": "fdc_id",
        "nutrient_id": "nutrient_id",
        "amount": "amount",
    },
    "nutrient": {
        "id": "id",
        "name": "name",
        "unit": "unit_name",
    },
    # USDA nutrient_id to our canonical name (from nutrient.name or id)
    # Common SR Legacy nutrient IDs: 1008=Energy, 1003=Protein, 1004=Fat, 1005=Carbs, etc.
    "nutrient_id_to_canonical": {
        1008: "energy_kcal",
        1003: "protein_g",
        1004: "total_fat_g",
        1005: "carbohydrates_g",
        1079: "fiber_g",
        2000: "sugars_g",
        1093: "sodium_mg",
        1092: "potassium_mg",
        1087: "calcium_mg",
        1089: "iron_mg",
        1106: "vitamin_a_iu",
        1162: "vitamin_c_mg",
        1253: "cholesterol_mg",
        1258: "saturated_fat_g",
    },
}


# ---------------------------------------------------------------------------
# Nutrition Daily Meals Dataset
# ---------------------------------------------------------------------------
MEALS_DIR = DATASETS_DIR / "meals"

def get_meals_paths():
    return {
        "dir": str(MEALS_DIR),
        "meals_file": str(MEALS_DIR / "meals.csv"),
        "daily_nutrition_file": str(MEALS_DIR / "daily_nutrition.csv"),
    }

# Map CSV column names to canonical nutrient names (case-insensitive match also supported in code)
MEALS_COLUMN_MAP = {
    "food_name": ["Food", "food", "food_name", "meal", "item", "name", "description"],
    "energy_kcal": ["Calories", "calories", "Energy", "energy_kcal", "kcal"],
    "protein_g": ["Protein (g)", "Protein", "protein", "protein_g"],
    "total_fat_g": ["Total Fat (g)", "Fat (g)", "Fat", "fat", "total_fat_g"],
    "carbohydrates_g": ["Carbohydrates (g)", "Carbs (g)", "Carbs", "carbohydrates_g", "Carbohydrate"],
    "fiber_g": ["Fiber (g)", "Fiber", "fiber_g"],
    "sugars_g": ["Sugars (g)", "Sugars", "sugars_g"],
    "sodium_mg": ["Sodium (mg)", "Sodium", "sodium_mg"],
}


# ---------------------------------------------------------------------------
# Diabetes and Blood Pressure Food Dataset
# ---------------------------------------------------------------------------
DISEASE_DIR = DATASETS_DIR / "disease"

def get_disease_paths():
    return {
        "dir": str(DISEASE_DIR),
        "food_disease_file": str(DISEASE_DIR / "food_disease.csv"),
        "diabetes_bp_foods_file": str(DISEASE_DIR / "diabetes_blood_pressure_food.csv"),
    }

DISEASE_COLUMN_MAP = {
    "food_name": ["Food", "food", "food_name", "item", "name", "Food Item"],
    "suitable_diabetes": ["Diabetes", "diabetes_safe", "suitable_diabetes", "Good for Diabetes", "diabetes"],
    "suitable_blood_pressure": ["Blood pressure", "bp_safe", "suitable_bp", "Blood Pressure", "hypertension"],
    "suitable_heart": ["Heart", "heart_safe", "suitable_heart", "Heart Disease", "heart"],
}


# ---------------------------------------------------------------------------
# Diet Recommendation Dataset
# ---------------------------------------------------------------------------
DIET_DIR = DATASETS_DIR / "diet_recommendation"

def get_diet_recommendation_paths():
    return {
        "dir": str(DIET_DIR),
        "diet_file": str(DIET_DIR / "diet_recommendation.csv"),
        "diet_dataset_file": str(DIET_DIR / "Diet_recommendation.csv"),
    }

DIET_COLUMN_MAP = {
    "food_name": ["Food", "food", "food_name", "name", "Item"],
    "diet_type": ["Diet", "diet_type", "Type", "Category", "Diet_type"],
    "recommendation_notes": ["Recommendation", "recommendation", "Notes", "description", "Veg_NonVeg"],
}
