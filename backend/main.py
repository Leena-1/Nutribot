"""
Nutribot FastAPI application.

Run:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.api import router
from backend.config import get_settings
from backend.utils.fastapi_app import register_exception_handlers
from backend.utils.logging import configure_logging
from backend.utils.rate_limit import RateLimitMiddleware

# Load settings
_settings = get_settings()

# Configure logging
configure_logging(level="INFO", json_logs=_settings.environment != "dev")

from contextlib import asynccontextmanager
import os
from backend.core.data_loader import data_loader
from backend.services.ml_trainer import train_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    try:
        # Load datasets (DataLoader instance creates them on initialization, 
        # but calling get methods ensures they are available)
        data_loader.get_nutribot_df()
        data_loader.get_indian_food_df()
        data_loader.get_exercise_df()
        data_loader.get_food_safety_df()
        
        # Train model if not exists
        model_path = "backend/models/risk_model.pkl"
        if not os.path.exists(model_path):
            print("risk_model.pkl not found, running ml_trainer...")
            train_model()
            
        print("Nutribot backend ready")
    except Exception as e:
        print(f"Startup error: {e}")
        
    yield
    # On shutdown
    print("Nutribot backend shutting down")

# Create single app instance
app = FastAPI(
    title="Nutribot API",
    description="AI Food Nutrition & Disease Risk Prediction",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (Flutter connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=_settings.rate_limit_per_minute
)

# Include central router
# This now includes food, chat, auth, and meal routes
app.include_router(router, prefix="/api")

# Exception handlers
register_exception_handlers(app)

# Root
@app.get("/")
def root():
    return {
        "service": "Nutribot API",
        "docs": "/docs",
        "health": "/health"
    }

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}
