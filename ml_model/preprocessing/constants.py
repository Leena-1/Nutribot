"""
Standard nutrient and unit definitions for the preprocessing pipeline.

All datasets are normalized to these canonical names and units
for the unified food feature table.
"""

# Canonical nutrient names in the unified table (snake_case)
STANDARD_NUTRIENT_COLUMNS = [
    "energy_kcal",
    "protein_g",
    "total_fat_g",
    "carbohydrates_g",
    "fiber_g",
    "sugars_g",
    "sodium_mg",
    "potassium_mg",
    "calcium_mg",
    "iron_mg",
    "vitamin_a_iu",
    "vitamin_c_mg",
    "cholesterol_mg",
    "saturated_fat_g",
]

# Maps common alternate names/units to (canonical_name, scale_to_standard_unit).
# scale_to_standard_unit: value_in_file * scale = value in standard unit
NUTRIENT_ALIASES = {
    # Energy
    "energy_kcal": ("energy_kcal", 1.0),
    "energy": ("energy_kcal", 1.0),
    "calories": ("energy_kcal", 1.0),
    "kcal": ("energy_kcal", 1.0),
    "energy_kj": ("energy_kcal", 0.239006),  # kJ to kcal
    # Protein
    "protein_g": ("protein_g", 1.0),
    "protein": ("protein_g", 1.0),
    # Fat
    "total_fat_g": ("total_fat_g", 1.0),
    "total lipid (fat)": ("total_fat_g", 1.0),
    "fat": ("total_fat_g", 1.0),
    "total_fat": ("total_fat_g", 1.0),
    "saturated_fat_g": ("saturated_fat_g", 1.0),
    "saturated fat": ("saturated_fat_g", 1.0),
    # Carbs
    "carbohydrates_g": ("carbohydrates_g", 1.0),
    "carbohydrate": ("carbohydrates_g", 1.0),
    "carbohydrates": ("carbohydrates_g", 1.0),
    "carbs": ("carbohydrates_g", 1.0),
    "fiber_g": ("fiber_g", 1.0),
    "fiber": ("fiber_g", 1.0),
    "sugars_g": ("sugars_g", 1.0),
    "sugars": ("sugars_g", 1.0),
    "sugars, total": ("sugars_g", 1.0),
    "sugar": ("sugars_g", 1.0),
    # Minerals (mg)
    "sodium_mg": ("sodium_mg", 1.0),
    "sodium": ("sodium_mg", 1.0),
    "na": ("sodium_mg", 1.0),
    "potassium_mg": ("potassium_mg", 1.0),
    "potassium": ("potassium_mg", 1.0),
    "k": ("potassium_mg", 1.0),
    "calcium_mg": ("calcium_mg", 1.0),
    "calcium": ("calcium_mg", 1.0),
    "iron_mg": ("iron_mg", 1.0),
    "iron": ("iron_mg", 1.0),
    # Vitamins
    "vitamin_a_iu": ("vitamin_a_iu", 1.0),
    "vitamin a": ("vitamin_a_iu", 1.0),
    "vitamin_c_mg": ("vitamin_c_mg", 1.0),
    "vitamin c": ("vitamin_c_mg", 1.0),
    # Cholesterol
    "cholesterol_mg": ("cholesterol_mg", 1.0),
    "cholesterol": ("cholesterol_mg", 1.0),
}

# Standard units for display and validation
STANDARD_UNITS = {
    "energy_kcal": "kcal",
    "protein_g": "g",
    "total_fat_g": "g",
    "carbohydrates_g": "g",
    "fiber_g": "g",
    "sugars_g": "g",
    "sodium_mg": "mg",
    "potassium_mg": "mg",
    "calcium_mg": "mg",
    "iron_mg": "mg",
    "vitamin_a_iu": "IU",
    "vitamin_c_mg": "mg",
    "cholesterol_mg": "mg",
    "saturated_fat_g": "g",
}

# Disease-related columns in unified table (from disease/diet datasets)
DISEASE_COLUMNS = [
    "suitable_diabetes",
    "suitable_blood_pressure",
    "suitable_heart",
    "diet_type",
    "recommendation_notes",
]

# Minimum required columns to keep a row in unified table (at least one identifier + one nutrient)
REQUIRED_ID_COLUMNS = ["food_name_normalized"]
