"""
Shared utilities for cleaning and standardizing data across datasets.
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple

from ml_model.preprocessing.constants import NUTRIENT_ALIASES, STANDARD_NUTRIENT_COLUMNS


def normalize_food_name(name: str) -> str:
    """
    Normalize food name for consistent merging across datasets.
    - Lowercase, strip whitespace, collapse multiple spaces.
    - Remove common punctuation that might differ between sources.
    """
    if not isinstance(name, str) or pd.isna(name):
        return ""
    s = name.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[,.]", "", s)
    return s


def find_column(candidates: List[str], columns: List[str]) -> Optional[str]:
    """
    Find first candidate that exists in columns (case-insensitive).
    Returns the actual column name as it appears in the DataFrame.
    """
    col_lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in col_lower:
            return col_lower[cand.lower()]
    return None


def map_nutrient_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map existing columns to canonical nutrient names using NUTRIENT_ALIASES.
    Renames columns and applies scale factors. Drops unmapped nutrient-like columns
    that we don't use. Does not add missing standard columns (caller can fill NaN).
    """
    result = {}
    for col in df.columns:
        col_str = str(col).strip()
        key = col_str.lower().strip()
        if key in NUTRIENT_ALIASES:
            canonical, scale = NUTRIENT_ALIASES[key]
            result[canonical] = df[col].astype(float, errors="ignore") * scale
        # Also try exact key from alias (e.g. "Protein (g)" might be "protein_g" in some datasets)
        for alias, (canonical, scale) in NUTRIENT_ALIASES.items():
            if alias.lower() == key and canonical not in result:
                result[canonical] = df[col].astype(float, errors="ignore") * scale
                break
    out = pd.DataFrame(result)
    # Preserve non-nutrient columns from df
    for c in df.columns:
        if c not in out.columns and str(c).strip().lower() not in [a.lower() for a in NUTRIENT_ALIASES]:
            out[c] = df[c]
    return out


def standardize_nutrient_units(series: pd.Series, nutrient_name: str) -> pd.Series:
    """
    Ensure a nutrient series is in standard units (no conversion here if already
    mapped via NUTRIENT_ALIASES). Can be extended for unit strings in data.
    """
    return pd.to_numeric(series, errors="coerce")


def ensure_standard_nutrient_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add missing standard nutrient columns as NaN so that merged table has consistent schema.
    """
    for col in STANDARD_NUTRIENT_COLUMNS:
        if col not in df.columns:
            df[col] = float("nan")
    return df


def safe_numeric(value) -> float:
    """Convert value to float; return NaN if not possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")
