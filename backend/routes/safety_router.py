from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
import joblib
import pandas as pd
import os

from backend.core.auth import get_current_user
from backend.utils.firestore_helper import get_user_profile

router = APIRouter()

# Activity level mapping from Task 3
ACTIVITY_MAP = {
    "Sedentary": 0,
    "Lightly Active": 0,
    "Low": 0,
    "Moderately Active": 1,
    "Moderate": 1,
    "Very Active": 2,
    "High": 2
}

RISK_MAP = {
    0: "Safe",
    1: "Caution",
    2: "Danger"
}

@router.post("/check-safety")
async def check_safety(
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    # Step 1 - Fetch user from Firestore
    user_profile = await get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Step 2 - Recalculate server-side
    cal_target = float(user_profile.get("calorie_target", 2000))
    cal_consumed = float(user_profile.get("calories_consumed", 0))
    fiber_target = float(user_profile.get("fiber_target", 25))
    fiber_consumed = float(user_profile.get("fiber_consumed", 0))
    sodium_limit = float(user_profile.get("sodium_limit", 2300))
    sodium_consumed = float(user_profile.get("sodium_consumed", 0))
    
    calorie_remaining = cal_target - cal_consumed
    fiber_remaining = fiber_target - fiber_consumed
    sodium_remaining = sodium_limit - sodium_consumed
    
    # Step 3 - Rule-based Safety Label
    safety_label = "Safe"
    if calorie_remaining < 0:
        safety_label = "Calorie limit exceeded"
    elif sodium_remaining < 0:
        safety_label = "Sodium limit exceeded"
    elif fiber_remaining == 0:
        safety_label = "Fiber limit reached"
    elif fiber_remaining < 2:
        safety_label = "Restricted – fiber limit critical"
    elif fiber_remaining < 5:
        safety_label = "Caution – low fiber budget"
        
    # Step 4 - ML prediction
    medical_condition = user_profile.get("medical_condition", "Healthy")
    ml_risk = "N/A"
    
    # ML features map
    # BMI, Activity_Level_Encoded, Calorie_Target, Calories_Consumed, Protein_Consumed, Carbs_Consumed, Fat_Consumed, Sugar_Consumed, Sodium_Consumed, Sodium_Limit
    if medical_condition in ["Hypertension", "Diabetes Type 2", "Healthy", "Diabetes"]:
        try:
            model_path = "backend/models/risk_model.pkl"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                
                # Build feature vector
                activity_str = user_profile.get("activity_level", "Sedentary")
                activity_encoded = ACTIVITY_MAP.get(activity_str, 0)
                
                features = pd.DataFrame([{
                    'BMI': float(user_profile.get("bmi", 22.0)),
                    'Activity_Level_Encoded': activity_encoded,
                    'Calorie_Target': cal_target,
                    'Calories_Consumed': cal_consumed,
                    'Protein_Consumed': float(user_profile.get("protein_consumed", 0)),
                    'Carbs_Consumed': float(user_profile.get("carbs_consumed", 0)),
                    'Fat_Consumed': float(user_profile.get("fat_consumed", 0)),
                    'Sugar_Consumed': float(user_profile.get("sugar_consumed", 0)),
                    'Sodium_Consumed': sodium_consumed,
                    'Sodium_Limit': sodium_limit
                }])
                
                pred = model.predict(features)[0]
                ml_risk = RISK_MAP.get(int(pred), "Safe")
        except Exception as e:
            print(f"Error predicting ML risk: {e}")
            ml_risk = "N/A"
            
    # Step 5 - Return
    needs_exercise = calorie_remaining <= 0
    
    message = "You are on track, keep it up!"
    if needs_exercise:
        message = "You've exceeded your calories. Time for some exercise!"
    elif safety_label != "Safe":
        message = f"Watch out: {safety_label}."
    elif ml_risk in ["Caution", "Danger"]:
        message = f"ML model flagged your diet as {ml_risk}. Please review your macros."
        
    return {
        "risk_level": ml_risk,
        "safety_label": safety_label,
        "calorie_remaining": calorie_remaining,
        "fiber_remaining": fiber_remaining,
        "sodium_remaining": sodium_remaining,
        "needs_exercise": needs_exercise,
        "message": message
    }
