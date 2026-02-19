"""Backend configuration and paths."""

from pathlib import Path

# Assume backend is at project_root/backend
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

UNIFIED_CSV = PROJECT_ROOT / "datasets" / "processed" / "unified_food_features.csv"
FOOD_CNN_DIR = PROJECT_ROOT / "ml_model" / "saved_models" / "food_cnn"
DISEASE_MODEL_DIR = PROJECT_ROOT / "ml_model" / "saved_models" / "disease_model"
