"""
Disease suitability prediction from nutrient features.

Uses the unified food feature table. Trains scikit-learn classifiers
for diabetes, blood pressure, and heart suitability (binary).
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

UNIFIED_CSV = PROJECT_ROOT / "datasets" / "processed" / "unified_food_features.csv"
SAVED_MODEL_DIR = PROJECT_ROOT / "ml_model" / "saved_models" / "disease_model"

# Feature columns (nutrients); target columns (disease suitability)
NUTRIENT_FEATURES = [
    "energy_kcal", "protein_g", "total_fat_g", "carbohydrates_g", "fiber_g", "sugars_g",
    "sodium_mg", "potassium_mg", "calcium_mg", "iron_mg", "vitamin_a_iu", "vitamin_c_mg",
    "cholesterol_mg", "saturated_fat_g",
]
TARGETS = ["suitable_diabetes", "suitable_blood_pressure", "suitable_heart"]


def load_unified_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load unified food features; fill missing nutrients with 0 for model."""
    path = csv_path or UNIFIED_CSV
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for c in NUTRIENT_FEATURES:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def train_disease_models(
    df: Optional[pd.DataFrame] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Train binary classifiers for each disease target.
    Uses RandomForest; persists models and feature list.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
    except ImportError:
        raise ImportError("Install scikit-learn: pip install scikit-learn")

    df = df if df is not None else load_unified_data()
    if df.empty:
        return {}

    output_dir = Path(output_dir or SAVED_MODEL_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    X = df[[c for c in NUTRIENT_FEATURES if c in df.columns]].copy()
    X = X.fillna(0)
    feature_names = list(X.columns)
    results = {}

    for target in TARGETS:
        if target not in df.columns:
            continue
        y = pd.to_numeric(df[target], errors="coerce")
        y = y.fillna(0).astype(int).clip(0, 1)
        if y.nunique() < 2:
            continue
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
        clf.fit(X_train, y_train)
        acc = clf.score(X_test, y_test)
        results[target] = {"accuracy": float(acc)}
        with open(output_dir / f"{target}.pkl", "wb") as f:
            pickle.dump(clf, f)

    with open(output_dir / "feature_names.json", "w", encoding="utf-8") as f:
        json.dump(feature_names, f)
    return results


def predict_disease(
    nutrient_dict: Dict[str, float],
    model_dir: Optional[Path] = None,
) -> Dict[str, int]:
    """
    Predict disease suitability from a dict of nutrient values (per 100g or serving).
    Returns e.g. {"suitable_diabetes": 1, "suitable_blood_pressure": 1, "suitable_heart": 0}.
    """
    model_dir = Path(model_dir or SAVED_MODEL_DIR)
    feature_path = model_dir / "feature_names.json"
    if not feature_path.exists():
        return {t: -1 for t in TARGETS}

    with open(feature_path, encoding="utf-8") as f:
        feature_names = json.load(f)

    X = np.array([[float(nutrient_dict.get(c, 0)) for c in feature_names]])
    out = {}
    for target in TARGETS:
        pkl_path = model_dir / f"{target}.pkl"
        if not pkl_path.exists():
            out[target] = -1
            continue
        with open(pkl_path, "rb") as f:
            clf = pickle.load(f)
        out[target] = int(clf.predict(X)[0])
    return out
