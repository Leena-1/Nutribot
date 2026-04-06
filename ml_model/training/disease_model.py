"""
Disease suitability prediction from nutrient features.

Uses the unified food feature table. Trains scikit-learn classifiers
for diabetes, blood pressure, and heart suitability (binary).
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

ENGINEERED_FEATURES = [
    "calorie_density",
    "sugar_ratio",
    "fat_ratio",
    "sodium_ratio",
]


def _safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    b = b.replace(0, np.nan)
    return (a / b).replace([np.inf, -np.inf], np.nan).fillna(0)


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features used for disease risk models.
    Assumes nutrients are per 100g (consistent with USDA standard tables).
    """
    df = df.copy()
    for c in NUTRIENT_FEATURES:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        else:
            df[c] = 0.0

    df["calorie_density"] = df["energy_kcal"] / 100.0
    df["sugar_ratio"] = _safe_div(df["sugars_g"], df["carbohydrates_g"])
    denom = (df["protein_g"] + df["carbohydrates_g"] + df["total_fat_g"]).replace(0, np.nan)
    df["fat_ratio"] = (df["total_fat_g"] / denom).replace([np.inf, -np.inf], np.nan).fillna(0)
    df["sodium_ratio"] = _safe_div(df["sodium_mg"], df["energy_kcal"])

    return df


def load_unified_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load unified food features; fill missing nutrients with 0 for model."""
    path = csv_path or UNIFIED_CSV
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = add_engineered_features(df)
    return df


def train_disease_models(
    df: Optional[pd.DataFrame] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Train binary classifiers for each disease target.
    Uses RandomForest; persists models and metadata (features + normalization stats).
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        from sklearn.model_selection import train_test_split
    except ImportError:
        raise ImportError("Install scikit-learn: pip install scikit-learn")

    df = df if df is not None else load_unified_data()
    if df.empty:
        return {}

    output_dir = Path(output_dir or SAVED_MODEL_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    feature_cols = [c for c in (NUTRIENT_FEATURES + ENGINEERED_FEATURES) if c in df.columns]
    X = df[feature_cols].copy()
    X = X.fillna(0)
    feature_names = list(X.columns)
    means = X.mean(axis=0).to_dict()
    stds = X.std(axis=0).replace(0, 1.0).to_dict()
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
        y_pred = clf.predict(X_test)
        results[target] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
        }
        with open(output_dir / f"{target}.pkl", "wb") as f:
            pickle.dump(clf, f)

    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "feature_names": feature_names,
                "means": means,
                "stds": stds,
                "metrics": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    return results


def _load_metadata(model_dir: Path) -> Optional[Dict[str, Any]]:
    meta = model_dir / "metadata.json"
    if not meta.exists():
        # backwards-compat: old format
        legacy = model_dir / "feature_names.json"
        if legacy.exists():
            with open(legacy, encoding="utf-8") as f:
                return {"feature_names": json.load(f), "means": {}, "stds": {}}
        return None
    with open(meta, encoding="utf-8") as f:
        return json.load(f)


def predict_disease(
    nutrient_dict: Dict[str, float],
    model_dir: Optional[Path] = None,
) -> Dict[str, int]:
    """
    Predict disease suitability from a dict of nutrient values (per 100g or serving).
    Returns e.g. {"suitable_diabetes": 1, "suitable_blood_pressure": 1, "suitable_heart": 0}.
    """
    model_dir = Path(model_dir or SAVED_MODEL_DIR)
    meta = _load_metadata(model_dir)
    if not meta:
        return {t: -1 for t in TARGETS}
    feature_names = meta.get("feature_names", [])
    X = np.array([[float(nutrient_dict.get(c, 0)) for c in feature_names]], dtype=float)
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


def predict_disease_risk(
    nutrient_dict: Dict[str, float],
    model_dir: Optional[Path] = None,
    *,
    top_k: int = 5,
) -> Dict[str, Dict[str, Any]]:
    """
    Predict disease risk probability and provide a lightweight explanation.

    Output example:
      {
        "suitable_diabetes": {"probability": 0.82, "label": 1, "top_factors": {"sugars_g": 0.41, ...}},
        ...
      }
    """
    model_dir = Path(model_dir or SAVED_MODEL_DIR)
    meta = _load_metadata(model_dir)
    if not meta:
        return {}
    feature_names: List[str] = meta.get("feature_names", [])
    means: Dict[str, float] = meta.get("means", {}) or {}
    stds: Dict[str, float] = meta.get("stds", {}) or {}

    x = np.array([float(nutrient_dict.get(c, 0)) for c in feature_names], dtype=float)
    X = x.reshape(1, -1)

    out: Dict[str, Dict[str, Any]] = {}
    for target in TARGETS:
        pkl_path = model_dir / f"{target}.pkl"
        if not pkl_path.exists():
            continue
        with open(pkl_path, "rb") as f:
            clf = pickle.load(f)

        if hasattr(clf, "predict_proba"):
            prob = float(clf.predict_proba(X)[0][1])
        else:
            prob = float(clf.predict(X)[0])
        label = int(prob >= 0.5)

        # Explanation proxy: abs(zscore) * feature_importance
        importances = getattr(clf, "feature_importances_", None)
        if importances is None or len(importances) != len(feature_names):
            top = {}
        else:
            z = np.array(
                [
                    (x[i] - float(means.get(feature_names[i], 0.0))) / float(stds.get(feature_names[i], 1.0) or 1.0)
                    for i in range(len(feature_names))
                ],
                dtype=float,
            )
            scores = np.abs(z) * np.array(importances, dtype=float)
            idxs = np.argsort(scores)[::-1][: max(1, int(top_k))]
            top = {feature_names[i]: float(scores[i]) for i in idxs if scores[i] > 0}

        out[target] = {"probability": prob, "label": label, "top_factors": top}

    return out
