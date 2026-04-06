from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
import pandas as pd

from backend.core.auth import get_current_user
from backend.utils.firestore_helper import get_user_profile
from backend.core.data_loader import data_loader

router = APIRouter()

@router.post("/recommend-exercise")
async def recommend_exercise(
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    df = data_loader.get_exercise_df()
    if df is None:
        raise HTTPException(status_code=500, detail="Exercise dataset not loaded")
        
    # Step 1 - Fetch user from Firestore
    user_profile = await get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Step 2 - Map BMI
    bmi = float(user_profile.get("bmi", 22.0))
    if bmi < 18.5:
        bmi_group = "Underweight(<18.5)"
    elif 18.5 <= bmi <= 24.9:
        bmi_group = "Normal(18.5-24.9)"
    elif 25.0 <= bmi <= 29.9:
        bmi_group = "Overweight(25-29.9)"
    else:
        bmi_group = "Obese(30+)"
        
    # Step 3 - Map activity_level
    act = user_profile.get("activity_level", "Sedentary")
    if act in ["Sedentary", "Low"]:
        act_level = "Sedentary"
    elif act == "Lightly Active":
        act_level = "Lightly Active"
    elif act in ["Moderately Active", "Moderate"]:
        act_level = "Moderately Active"
    elif act in ["Very Active", "High"]:
        act_level = "Very Active"
    else:
        act_level = "Sedentary"
        
    # Step 4 - Filter exercise dataset
    medical_condition = user_profile.get("medical_condition", "Healthy")
    
    # Fill Nans just in case
    df = df.copy()
    df["Suitable Activity Levels"] = df.get("Suitable Activity Levels", pd.Series(dtype=str)).fillna("")
    df["Medical Caution"] = df.get("Medical Caution", pd.Series(dtype=str)).fillna("")
    df["BMI Group"] = df.get("BMI Group", pd.Series(dtype=str)).fillna("")
    
    filtered_df = df[df["BMI Group"].str.contains(bmi_group, regex=False, na=False)]
    
    # Filter by Suitable Activity Levels
    mask_act = filtered_df["Suitable Activity Levels"].str.contains(act_level, regex=False, na=False) | \
               (filtered_df["Suitable Activity Levels"] == "All")
    filtered_df = filtered_df[mask_act]
    
    # Filter by Medical Caution (exclude if contains user's condition)
    if medical_condition != "Healthy":
        mask_med = ~filtered_df["Medical Caution"].str.contains(medical_condition, regex=False, na=False)
        filtered_df = filtered_df[mask_med]
        
    if filtered_df.empty:
        return []
        
    # Step 5 - Sort by Calories Burned (kcal) descending
    col_cal = "Calories Burned (kcal)" if "Calories Burned (kcal)" in filtered_df.columns else "Calories Burned"
    if col_cal in filtered_df.columns:
        # ensure numeric
        filtered_df[col_cal] = pd.to_numeric(filtered_df[col_cal], errors='coerce').fillna(0)
        filtered_df = filtered_df.sort_values(by=col_cal, ascending=False)
        
    # Step 6 - Return top 3
    results = []
    top_3 = filtered_df.head(3)
    
    for _, row in top_3.iterrows():
        results.append({
            "exercise_name": row.get("Exercise Name", "Unknown Exercise"),
            "category": row.get("Category", "General"),
            "duration_min": row.get("Duration (min)", 30),
            "calories_burned": row.get(col_cal, 0),
            "intensity": row.get("Intensity", "Moderate"),
            "notes": row.get("Notes", "")
        })
        
    return results
