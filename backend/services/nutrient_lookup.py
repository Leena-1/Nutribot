"""
Look up nutrient and disease info by food name from the unified table.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.config import UNIFIED_CSV

# Normalize for lookup: lowercase, strip, single spaces
def _normalize(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    return " ".join(name.lower().strip().split()).replace(",", "").replace(".", "")


def load_unified_table(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load unified food features CSV."""
    path = csv_path or UNIFIED_CSV
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def lookup_food(
    food_name: str,
    df: Optional[pd.DataFrame] = None,
) -> Optional[Dict[str, Any]]:
    """
    Look up a food by name. Tries exact normalized match first, then contains.
    Returns one row as dict with nutrient and disease fields.
    """
    if df is None:
        df = load_unified_table()
    if df.empty:
        return None

    key = _normalize(food_name)
    if "food_name_normalized" in df.columns:
        df = df.copy()
        df["_norm"] = df["food_name_normalized"].fillna("").astype(str).map(_normalize)
        match = df[df["_norm"] == key]
        if match.empty:
            match = df[df["_norm"].str.contains(key, na=False, regex=False)]
        if match.empty:
            match = df[df["food_name"].fillna("").astype(str).str.lower().str.contains(key, na=False, regex=False)]
    else:
        match = df[df["food_name"].fillna("").astype(str).str.lower().str.contains(key, na=False, regex=False)]

    if match.empty:
        return None
    row = match.iloc[0]
    out = row.to_dict()
    if "_norm" in out:
        del out["_norm"]
    for k, v in out.items():
        if pd.isna(v):
            out[k] = None
        elif isinstance(v, (float, int)) and isinstance(row.get(k), (float, int)):
            out[k] = v
    return out


def get_nutrient_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a clean nutrient summary for API response."""
    nutrient_cols = [
        "energy_kcal", "protein_g", "total_fat_g", "carbohydrates_g", "fiber_g", "sugars_g",
        "sodium_mg", "potassium_mg", "calcium_mg", "iron_mg", "vitamin_a_iu", "vitamin_c_mg",
        "cholesterol_mg", "saturated_fat_g",
    ]
    summary = {}
    for c in nutrient_cols:
        v = row.get(c)
        if v is not None and (isinstance(v, (int, float)) or (isinstance(v, str) and v.strip())):
            try:
                summary[c] = float(v)
            except (TypeError, ValueError):
                pass
    return summary


def get_disease_flags(row: Dict[str, Any]) -> Dict[str, Any]:
    """Extract disease suitability flags for API response."""
    flags = {}
    for t in ("suitable_diabetes", "suitable_blood_pressure", "suitable_heart"):
        v = row.get(t)
        if v is not None:
            try:
                flags[t] = int(float(v))
            except (TypeError, ValueError):
                flags[t] = -1
        else:
            flags[t] = -1
    return flags
