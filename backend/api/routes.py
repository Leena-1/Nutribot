"""
FastAPI routes: predict_food, chat_query.
Optimized for performance with async processing and image optimization.
"""

import io
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

# Add project root for ML imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import DISEASE_MODEL_DIR, FOOD_CNN_DIR, UNIFIED_CSV
from backend.services.chat_service import chat_response
from backend.services.image_processor import preprocess_image, resize_for_model
from backend.services.nutrient_lookup import (
    get_disease_flags,
    get_nutrient_summary,
    lookup_food,
    load_unified_table,
)

router = APIRouter()

# Lazy-loaded model and table
_food_model = None
_class_names = None
_unified_df = None
_disease_models_loaded = None


async def _get_food_prediction(image_bytes: bytes) -> Optional[str]:
    """
    Run CNN on image asynchronously; return food class name or None if model missing.
    Optimized with image preprocessing and async execution.
    """
    global _food_model, _class_names
    if not FOOD_CNN_DIR.exists():
        return None
    try:
        import numpy as np
        import tensorflow as tf
        from ml_model.training.food_cnn import IMG_SIZE, load_saved_model

        # Load model if not already loaded (lazy loading)
        if _food_model is None:
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            _food_model, _class_names = await loop.run_in_executor(
                None, load_saved_model, FOOD_CNN_DIR
            )
        
        if _food_model is None or not _class_names:
            return None

        # Preprocess image in thread pool
        loop = asyncio.get_event_loop()
        img_array = await loop.run_in_executor(
            None, resize_for_model, image_bytes, IMG_SIZE
        )
        
        # Convert to TensorFlow tensor and preprocess
        def _run_inference(img_arr):
            img = tf.constant(img_arr, dtype=tf.float32)
            img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
            img = tf.expand_dims(img, 0)
            return _food_model.predict(img, verbose=0)
        
        # Run inference in thread pool (TensorFlow operations can block)
        logits = await loop.run_in_executor(
            None, _run_inference, img_array
        )
        
        idx = int(np.argmax(logits[0]))
        name = _class_names[idx] if idx < len(_class_names) else None
        return name.replace("_", " ") if name else None
    except Exception as e:
        print(f"Food prediction error: {e}")
        return None


def _get_unified_df():
    global _unified_df
    if _unified_df is None:
        _unified_df = load_unified_table()
    return _unified_df


def _predict_disease_from_nutrients(nutrient_dict: Dict[str, float]) -> Dict[str, int]:
    """Run disease models if available."""
    if not DISEASE_MODEL_DIR.exists():
        return {}
    try:
        from ml_model.training.disease_model import predict_disease
        return predict_disease(nutrient_dict, DISEASE_MODEL_DIR)
    except Exception:
        return {}


# --- Request/Response models ---

class ChatQueryBody(BaseModel):
    query: str
    user_context: Optional[str] = None


# --- Endpoints ---

@router.post("/predict_food")
async def predict_food(
    file: Optional[UploadFile] = File(None),
    food_name: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """
    Predict food from image and return nutrients + disease suitability.
    Optimized with async processing and image preprocessing.
    Either upload an image (file) or provide food_name for lookup only.
    """
    # Load unified table (cached after first load)
    df = _get_unified_df()
    if df.empty:
        raise HTTPException(status_code=503, detail="Unified food table not loaded. Run preprocessing.")

    detected_name = None
    if file and file.filename:
        content = await file.read()
        if content:
            # Preprocess image for faster ML inference
            loop = asyncio.get_event_loop()
            optimized_image = await loop.run_in_executor(
                None, preprocess_image, content
            )
            # Run food detection asynchronously
            detected_name = await _get_food_prediction(optimized_image)
    
    name_to_lookup = (detected_name or food_name or "").strip()
    if not name_to_lookup:
        return {
            "food_name": None,
            "detected_from_image": False,
            "message": "Provide an image (file) or food_name for lookup.",
            "nutrients": {},
            "disease_suitability": {},
        }

    # Lookup food (fast operation, no need for async)
    row = lookup_food(name_to_lookup, df)
    if row is None:
        return {
            "food_name": name_to_lookup,
            "detected_from_image": bool(detected_name),
            "message": "Food not found in database.",
            "nutrients": {},
            "disease_suitability": {},
        }

    # Extract nutrients and disease flags
    nutrients = get_nutrient_summary(row)
    disease_flags = get_disease_flags(row)
    
    # Run disease prediction if needed (in thread pool if heavy)
    if nutrients and disease_flags.get("suitable_diabetes") == -1:
        loop = asyncio.get_event_loop()
        predicted_flags = await loop.run_in_executor(
            None, _predict_disease_from_nutrients, nutrients
        )
        if predicted_flags:
            disease_flags.update(predicted_flags)

    # Return optimized response (only necessary fields)
    return {
        "food_name": row.get("food_name") or name_to_lookup,
        "detected_from_image": bool(detected_name),
        "nutrients": nutrients,
        "disease_suitability": disease_flags,
        "diet_type": row.get("diet_type"),
        "recommendation_notes": row.get("recommendation_notes"),
    }


@router.post("/chat_query")
async def chat_query(body: ChatQueryBody) -> Dict[str, Any]:
    """
    Handle chatbot questions about food safety and health impact.
    Optimized with async processing and personalized responses.
    """
    # Run chat response in thread pool (in case it becomes heavy with LLM)
    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(
        None,
        lambda: chat_response(body.query, user_context=body.user_context)
    )
    return {"query": body.query, "response": reply}
