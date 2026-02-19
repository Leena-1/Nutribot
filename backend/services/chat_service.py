"""
Simple rule-based chat responses for food safety and health impact questions.
Can be replaced or augmented with an LLM later.
"""

import re
from typing import Any, Dict, Optional

# Template responses keyed by keywords (lowercase)
CHAT_RULES = [
    (r"\b(sodium|salt)\b", "High sodium can raise blood pressure. Choose low-sodium options when possible."),
    (r"\b(sugar|sugars|sweet)\b", "Excess sugar can affect blood glucose and weight. Moderation is key for diabetes and heart health."),
    (r"\b(diabetes|diabetic)\b", "For diabetes, focus on high fiber, low added sugars, and controlled portions. Many vegetables and whole grains are suitable."),
    (r"\b(blood pressure|hypertension|bp)\b", "For blood pressure, reduce sodium and increase potassium (e.g. fruits, vegetables). Limit processed foods."),
    (r"\b(heart|cholesterol|fat)\b", "Heart health benefits from less saturated fat and trans fat, more fiber and omega-3s. Limit fried and processed foods."),
    (r"\b(calories|energy|weight)\b", "Balancing calories with activity helps weight management. Nutrient-dense foods give more nutrition per calorie."),
    (r"\b(protein|meat|chicken|fish)\b", "Lean proteins (chicken, fish, legumes) support muscle and satiety. Grill or bake instead of frying."),
    (r"\b(safe|unsafe|avoid|bad)\b", "Whether a food is safe depends on your conditions and portion. Use the app's disease suitability for your profile."),
    (r"\b(healthy|healthier|recommend)\b", "Healthier choices often include more vegetables, whole grains, and less added sugar and sodium. Check the diet recommendations in the app."),
]


def chat_response(query: str, context: Optional[Dict[str, Any]] = None, user_context: Optional[str] = None) -> str:
    """
    Return a text response to a user food/health query.
    context can include recent food result for personalized answers.
    user_context contains user profile info (name, age, gender, disease type).
    """
    if not query or not query.strip():
        return "Ask me about food, nutrients, or how foods affect diabetes, blood pressure, or heart health."

    q = query.lower().strip()
    
    # Extract disease type from user context if available
    disease_type = None
    if user_context:
        if 'diabetes' in user_context.lower():
            disease_type = 'diabetes'
        elif 'blood pressure' in user_context.lower() or 'hypertension' in user_context.lower():
            disease_type = 'blood_pressure'
        elif 'heart' in user_context.lower():
            disease_type = 'heart'
    
    # Personalized responses based on user context
    personalized_prefix = ""
    if disease_type:
        if disease_type == 'diabetes':
            personalized_prefix = "Based on your diabetes condition, "
        elif disease_type == 'blood_pressure':
            personalized_prefix = "Given your blood pressure concerns, "
        elif disease_type == 'heart':
            personalized_prefix = "For your heart health, "
    
    # Match query patterns
    for pattern, response in CHAT_RULES:
        if re.search(pattern, q):
            # Enhance response with personalization
            if disease_type:
                if disease_type == 'diabetes' and 'diabetes' in pattern:
                    return personalized_prefix + response
                elif disease_type == 'blood_pressure' and ('blood pressure' in pattern or 'sodium' in pattern):
                    return personalized_prefix + response
                elif disease_type == 'heart' and 'heart' in pattern:
                    return personalized_prefix + response
            
            return personalized_prefix + response if personalized_prefix else response

    # Default response with personalization
    default_response = (
        "I can help with questions about nutrients, diabetes, blood pressure, and heart health. "
        "Try asking about sodium, sugar, or whether a food is suitable for your condition."
    )
    
    if personalized_prefix:
        return personalized_prefix + "I recommend focusing on foods suitable for your condition. " + default_response
    
    return default_response
