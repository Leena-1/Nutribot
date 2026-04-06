from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from rapidfuzz import process, fuzz
import math

# Assuming get_current_user dependencies exist in existing routes
from backend.core.auth import get_current_user
from backend.core.data_loader import data_loader

router = APIRouter()

@router.post("/search-food")
async def search_food(
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    food_name = payload.get("food_name", "").strip()
    medical_condition = payload.get("medical_condition", "Healthy")
    diet_type = payload.get("diet_type", "Omnivore")

    if not food_name:
        raise HTTPException(status_code=400, detail="food_name is required")

    df = data_loader.get_indian_food_df()
    if df is None:
        raise HTTPException(status_code=500, detail="Indian food dataset not loaded")

    # Clean the dataset for missing numerical strings
    import pandas as pd

    # Step 1 — Fuzzy match against "Food Item" column
    food_items = df["Food Item"].dropna().tolist()
    
    # Rapidfuzz extract module
    matches = process.extract(food_name, food_items, scorer=fuzz.WRatio, limit=5)
    
    # Check top match score
    if not matches:
        raise HTTPException(status_code=404, detail="Food not found")
        
    top_match, top_score, _ = matches[0]
    
    did_you_mean = False
    matched_foods_df = pd.DataFrame()

    if top_score >= 80:
        matched_foods_df = df[df["Food Item"] == top_match]
    elif top_score >= 60:
        did_you_mean = True
        matched_foods_df = df[df["Food Item"] == top_match]
    else:
        # Check against Category
        category_matches = process.extract(food_name, df["Category"].dropna().unique().tolist(), scorer=fuzz.WRatio, limit=1)
        if category_matches and category_matches[0][1] >= 80:
            matched_category = category_matches[0][0]
            matched_foods_df = df[df["Category"] == matched_category]
        else:
            raise HTTPException(status_code=404, detail="Food not found")

    if matched_foods_df.empty:
        raise HTTPException(status_code=404, detail="Food not found")

    # Fill NaNs for tags and macros
    matched_foods_df = matched_foods_df.copy()
    matched_foods_df["Health Tags"] = matched_foods_df.get("Health Tags", pd.Series(dtype=str)).fillna("")
    matched_foods_df["Category"] = matched_foods_df.get("Category", pd.Series(dtype=str)).fillna("")
    matched_foods_df["Veg_NonVeg"] = matched_foods_df.get("Veg_NonVeg", pd.Series(dtype=str)).fillna("")
    
    def safe_float(val):
        try:
            return float(val)
        except:
            return 0.0

    # Step 2 & 3 - Filtering logic
    filtered_results = []
    
    for _, row in matched_foods_df.iterrows():
        # Read nutritional values
        gi_index = safe_float(row.get("Glycemic Index", 0))
        cholesterol = safe_float(row.get("Cholesterol (mg)", 0))
        fat = safe_float(row.get("Fat (g)", 0))
        sodium = safe_float(row.get("Sodium (mg)", 0))
        protein = safe_float(row.get("Protein (g)", 0))
        carbs = safe_float(row.get("Carbohydrates (g)", 0))
        
        health_tags = str(row.get("Health Tags", "")).lower()
        category = str(row.get("Category", "")).title()
        veg_nonveg = str(row.get("Veg_NonVeg", "")).title()
        
        disease_warning = None
        disease_skip = False
        
        # Step 2: Apply disease filters
        if medical_condition == "Diabetes Type 2":
            if not (gi_index < 55 or "diabetic-friendly" in health_tags):
                disease_skip = True
            elif gi_index >= 50 and gi_index < 55:
                disease_warning = "Borderline GI for Diabetes Type 2"
                
        elif medical_condition == "Heart Disease":
            if not (cholesterol < 50 and fat < 10):
                disease_skip = True
            elif cholesterol >= 40 or fat >= 8:
                disease_warning = "Borderline Fat/Cholesterol for Heart Disease"
                
        elif medical_condition == "Hypertension":
            if not (sodium < 400):
                disease_skip = True
            elif sodium >= 300:
                disease_warning = "Borderline Sodium for Hypertension"
                
        elif medical_condition == "Kidney Disease":
            if not (protein < 8 and sodium < 300):
                disease_skip = True
            elif protein >= 6 and sodium >= 250:
                disease_warning = "Borderline for Kidney Disease"
                
        elif medical_condition == "Celiac Disease":
            if category in ["Indian Bread", "Pasta", "Grain", "Bread"]:
                disease_skip = True
                
        elif medical_condition == "Crohn's Disease" or medical_condition == "IBS":
            if "low-fodmap" not in health_tags:
                disease_skip = True
                
        if disease_skip:
            continue
            
        # Step 3: Apply diet_type filter
        diet_skip = False
        
        if diet_type == "Vegan":
            if veg_nonveg != "Veg" or "dairy" in health_tags or "egg" in health_tags:
                diet_skip = True
        elif diet_type == "Vegetarian":
            if veg_nonveg != "Veg":
                diet_skip = True
        elif diet_type in ["Gluten-Free", "Celiac"]:
            if category in ["Indian Bread", "Pasta", "Grain", "Bread"]:
                diet_skip = True
        elif diet_type == "Keto":
            if carbs >= 10:
                diet_skip = True
        elif diet_type == "Low-FODMAP":
            if "low-fodmap" not in health_tags:
                diet_skip = True
        elif diet_type == "Diabetic-Friendly":
            if not (gi_index < 55 or "diabetic-friendly" in health_tags):
                diet_skip = True
                
        if diet_skip:
            continue

        # If it passes, format result
        result = row.to_dict()
        # Convert nan floats to None for JSON compliance
        for k, v in result.items():
            if type(v) == float and math.isnan(v):
                result[k] = None
                
        result["did_you_mean"] = did_you_mean
        if disease_warning:
            result["disease_warning"] = disease_warning
            
        filtered_results.append(result)

    # Note: If no foods pass the disease/diet filters but the food was found
    if not filtered_results and not matched_foods_df.empty:
        # Fallback behaviour: just return the raw item with a warning
        fallback = matched_foods_df.iloc[0].to_dict()
        for k, v in fallback.items():
            if type(v) == float and math.isnan(v):
                fallback[k] = None
        fallback["did_you_mean"] = did_you_mean
        fallback["disease_warning"] = f"This food doesn't match your {medical_condition} or {diet_type} filters."
        filtered_results.append(fallback)

    return filtered_results[:5]
