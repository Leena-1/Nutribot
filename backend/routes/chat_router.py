from fastapi import APIRouter, Depends
from rapidfuzz import process, fuzz
import pandas as pd
import re
import math
from typing import List, Dict, Any

from backend.schemas.chat import ChatRequest, ChatResponse, FoodResult
from backend.core.auth import get_current_user
from backend.utils.firestore_helper import get_user_profile
from backend.core.data_loader import data_loader

router = APIRouter()

def clean_float(val) -> float:
    try:
        if pd.isna(val) or val == "" or val is None:
            return 0.0
        return float(val)
    except:
        return 0.0

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Step 1: Fetch user profile
        uid = payload.user_id
        profile = await get_user_profile(uid)
        if not profile:
            return ChatResponse(
                reply="I couldn't load your profile. Please try again later.",
                intent="error",
                needs_exercise=False
            )

        # Step 2: Extract details
        msg = payload.message.lower().strip()
        user_name = profile.get("full_name", "Friend").split()[0]
        
        # Friendly Greetings
        GREETINGS = ["hi", "hello", "namaste", "hey", "hola", "yo"]
        if msg in GREETINGS:
            reply = f"Namaste {user_name}! 🙏 I'm your Nutribot. How can I help you stay healthy today with your {medical_condition} management?"
            return ChatResponse(reply=reply, intent="greeting")

        df = data_loader.get_indian_food_df()
        
        # Helper: Extract food names & Check rapidfuzz
        food_items = df["Food Item"].dropna().tolist() if df is not None else []
        best_match = None
        best_score = 0
        if df is not None:
            res = process.extract(msg, food_items, scorer=fuzz.WRatio, limit=1)
            if res:
                best_match, best_score, _ = res[0]

        # Step 3: Intent Detection
        intent = "fallback"
        
        if payload.intent_hint == "scan_result" or any(w in msg for w in ["scan", "scanned", "label", "nutrition facts", "calculate nutrient"]):
            intent = "scan_result"
        elif any(w in msg for w in ["can i eat", "is it safe", "should i eat", "safe to eat", "kha sakta", "khana", "khana chahiye"]) or (best_score >= 80 and len(msg.split()) < 4):
            intent = "food_query"
        elif any(w in msg for w in ["what should i eat", "what can i eat", "my disease", "my condition", "diet for", "food for", "recommend", "suggest", "safe food", "health tips"]):
            intent = "disease_diet_query"
        elif any(w in msg for w in ["calorie", "calories", "how much left", "daily limit", "budget", "kcal", "consumption"]):
            intent = "calorie_check"

        # User limits
        cal_target = float(profile.get("calorie_target", 2000))
        cal_cons = float(profile.get("calories_consumed", 0))
        sodium_limit = float(profile.get("sodium_limit", 2300))
        sodium_cons = float(profile.get("sodium_consumed", 0))
        fiber_target = float(profile.get("fiber_target", 25))
        fiber_cons = float(profile.get("fiber_consumed", 0))
        
        medical_condition = profile.get("medical_condition", "Healthy")
        diet_type = profile.get("diet_type", "Omnivore")
        
        # Step 4: Execute Intent

        if intent == "scan_result":
            def ext(pat):
                m = re.search(pat, payload.message, re.IGNORECASE)
                return float(m.group(1)) if m else 0.0

            p_cal = ext(r'calories\s*[:\-]?\s*([\d\.]+)')
            p_pro = ext(r'protein\s*[:\-]?\s*([\d\.]+)')
            p_crb = ext(r'carbs\s*[:\-]?\s*([\d\.]+)')
            p_fat = ext(r'fat\s*[:\-]?\s*([\d\.]+)')
            p_sod = ext(r'sodium\s*[:\-]?\s*([\d\.]+)')
            p_fib = ext(r'fiber\s*[:\-]?\s*([\d\.]+)')
            
            if p_cal == 0 and p_pro == 0 and p_crb == 0 and p_fat == 0:
                return ChatResponse(
                    reply="I couldn't quite catch those numbers. Please ensure the nutrition label is clear in the scan! 📸",
                    intent="scan_result"
                )

            rem_cal = cal_target - (cal_cons + p_cal)
            
            reply = f"Scan successful! ✅\nCalories: {p_cal} kcal | Protein: {p_pro}g | Fat: {p_fat}g\n"
            reply += f"Sodium: {p_sod}mg | Fiber: {p_fib}g\n\n"
            reply += f"Based on your profile, you have {round(rem_cal, 1)} kcal remaining for today. "
            
            if rem_cal > 200:
                reply += "Yeh toh badiya hai! You have room for a healthy snack. 🍏"
            elif rem_cal > 0:
                reply += "Kaafi pass hain limit ke! Be careful with your next meal. ⚠️"
            else:
                reply += "Oh no! You've crossed your calorie limit. 🛑 Time for a 30-min walk to burn around 133 kcal!"

            return ChatResponse(reply=reply, intent="scan_result", needs_exercise=(rem_cal <= 0))

        elif intent == "food_query":
            if df is None or df.empty:
                return ChatResponse(reply="Sorry, my food database is resting right now. Try again in a bit! 😴", intent="error")
                
            clean_msg = payload.message.lower()
            FOOD_QUERY_TRIGGERS = ["can i eat", "can i have", "is it safe", "eat", "should i eat", "safe to eat", "kha sakta", "khana", "nutrition", "calories in", "how much", "tell me about"]
            for phrase in FOOD_QUERY_TRIGGERS:
                clean_msg = clean_msg.replace(phrase, "").strip()
            
            food_name = clean_msg.strip(" ?!")
            if not food_name: food_name = payload.message.lower()
            
            results = process.extract(food_name, df["Food Item"].tolist(), scorer=fuzz.WRatio, limit=5)
            
            if not results or results[0][1] < 60:
                return ChatResponse(reply=f"I couldn't find '{food_name}' in my list of Indian foods. 🔍 Try searching for something like 'Poha', 'Dal', or 'Roti'!", intent="food_query")
            
            best_match_name = results[0][0]; f_score = results[0][1]
            food_row = df[df["Food Item"] == best_match_name].iloc[0]
            
            cal = food_row.get("Calories kcal", 0); protein = food_row.get("Protein g", 0)
            carbs = food_row.get("Carbohydrates g", 0); fat = food_row.get("Fat g", 0)
            sodium = food_row.get("Sodium mg", 0); gi = food_row.get("GI Index", 0)
            health_tags = str(food_row.get("Health Tags", "")); cholesterol = food_row.get("Cholesterol mg", 0)
            fiber = food_row.get("Fiber g", 0); category = str(food_row.get("Category", "")).lower()
            meal_type = str(food_row.get("Meal Type", "Any")); vn = str(food_row.get("Veg NonVeg", "Veg"))
            
            warning = None
            if medical_condition == "Diabetes Type 2" and clean_float(gi) >= 55:
                warning = f"Caution! {best_match_name} has a high GI ({gi}). Since you're managing Diabetes, it's safer to avoid this or eat in moderation with high fiber. 🩺"
            elif medical_condition == "Heart Disease" and (clean_float(cholesterol) >= 50 or clean_float(fat) >= 10):
                warning = f"Heart check! {best_match_name} is high in fats/cholesterol. For your heart health, try something lighter. ❤️"
            elif medical_condition == "Hypertension" and clean_float(sodium) >= 400:
                warning = f"Sodium Alert! {best_match_name} has {sodium}mg sodium. This might increase your blood pressure. 🧂"
            
            if warning:
                reply = f"{warning}\n\nNutrition:\n{cal} kcal | {protein}g Protein | {fat}g Fat\n\nSafer options for you: "
                # Add safe alternatives from dataset later if possible, for now focus on tone
                reply += "Moong Dal, Brown Rice, or a fresh salad! 🥗"
            else:
                reply = f"Haan ji! {best_match_name} is perfectly safe for your {medical_condition} condition. ✅\n\nNutrition:\n{cal} kcal | {protein}g Protein | {fat}g Fat | {sodium}mg Sodium"
            
            fr = FoodResult(
                food_item=best_match_name, calories_kcal=clean_float(cal), protein_g=clean_float(protein),
                carbs_g=clean_float(carbs), fat_g=clean_float(fat), fiber_g=clean_float(fiber),
                sodium_mg=clean_float(sodium), cholesterol_mg=clean_float(cholesterol), gi_index=clean_float(gi) if gi != 0 else None,
                meal_type=meal_type, health_tags=health_tags, veg_nonveg=vn, did_you_mean=(f_score < 80), disease_warning=warning
            )
            return ChatResponse(reply=reply, intent="food_query", foods=[fr])

        elif intent == "disease_diet_query":
            reply = f"For your {medical_condition} condition and {diet_type} diet, here's a healthy mini-plan for today: 📝\n\n"
            reply += "• Breakfast: Oats or Sprouts (High fiber, steady energy)\n"
            reply += "• Lunch: Roti with Green Vegetables & Dal (Protein packed)\n"
            reply += "• Dinner: Light Khichdi or Grilled Tofu (Easy to digest)\n\n"
            reply += "Keep drinking plenty of water! 💧 Would you like nutrition facts for any specific dish?"
            return ChatResponse(reply=reply, intent="disease_diet_query")

        elif intent == "calorie_check":
            rem_cal = cal_target - cal_cons
            reply = f"Current Status: {cal_cons} kcal consumed / {cal_target} kcal target. 🎯\n"
            reply += f"You have {round(rem_cal, 1)} kcal left for today.\n\n"
            if rem_cal > 0: reply += "Balance bana ke chalein! You're doing great. 👍"
            else: reply += "Over-limit alert! 🛑 Try some light exercise now."
            return ChatResponse(reply=reply, intent="calorie_check", needs_exercise=(rem_cal <= 0))

        # fallback
        reply = f"I'm still learning, {user_name}! 😅 But I can help with:\n• Checking if a food is safe ('Is samosa okay for me?')\n• Giving diet advice for {medical_condition}.\n• Checking your remaining daily calories.\n\nTry asking about a specific Indian dish! 🍲"
        return ChatResponse(reply=reply, intent="fallback")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ChatResponse(
            reply="Something went wrong on my end. Please try again.",
            intent="error",
            needs_exercise=False
        )
