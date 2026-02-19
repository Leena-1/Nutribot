"""
Merge pipeline: combine cleaned datasets into a unified food feature table.

- Merges on food_name_normalized (outer join so we keep all foods from any source)
- Standardizes nutrient units (already done in processors)
- Outputs one CSV: unified_food_features.csv
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional

from ml_model.preprocessing.config import (
    PROCESSED_DIR,
    ensure_processed_dir,
    get_usda_paths,
    get_meals_paths,
    get_disease_paths,
    get_diet_recommendation_paths,
)
from ml_model.preprocessing.constants import (
    STANDARD_NUTRIENT_COLUMNS,
    DISEASE_COLUMNS,
    REQUIRED_ID_COLUMNS,
)
from ml_model.preprocessing.usda_processor import USDAProcessor
from ml_model.preprocessing.meals_processor import MealsProcessor
from ml_model.preprocessing.disease_processor import DiseaseProcessor
from ml_model.preprocessing.diet_recommendation_processor import DietRecommendationProcessor
from ml_model.preprocessing.utils import ensure_standard_nutrient_columns


# Output column order for unified table
UNIFIED_COLUMNS = (
    ["food_name", "food_name_normalized", "source_datasets"]
    + STANDARD_NUTRIENT_COLUMNS
    + DISEASE_COLUMNS
)


def _ensure_columns(df: pd.DataFrame, required: List[str]) -> pd.DataFrame:
    """Add missing columns as NaN."""
    for c in required:
        if c not in df.columns:
            df[c] = float("nan")
    return df


def _ensure_string_normalized(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure food_name_normalized is string type for merge (avoid float64 vs object mismatch)."""
    df = df.copy()
    if "food_name_normalized" not in df.columns:
        return df
    df["food_name_normalized"] = df["food_name_normalized"].fillna("").astype(str)
    df["food_name_normalized"] = df["food_name_normalized"].replace("nan", "")
    return df


def _select_and_tag(
    df: pd.DataFrame,
    source_name: str,
    nutrient_cols: List[str],
    disease_cols: List[str],
) -> pd.DataFrame:
    """Keep only needed columns and add source tag."""
    keep = ["food_name", "food_name_normalized"] + nutrient_cols + disease_cols
    existing = [c for c in keep if c in df.columns]
    out = df[existing].copy()
    out = _ensure_columns(out, keep)
    out["source_datasets"] = source_name
    out = _ensure_string_normalized(out)
    return out[["food_name", "food_name_normalized", "source_datasets"] + nutrient_cols + disease_cols]


def _merge_two(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Outer merge two frames on food_name_normalized; coalesce overlapping columns."""
    left = _ensure_string_normalized(left)
    right = _ensure_string_normalized(right)
    merged = left.merge(
        right,
        on="food_name_normalized",
        how="outer",
        suffixes=("_x", "_y"),
    )
    # Coalesce food_name and nutrient/disease columns; combine source_datasets
    for c in ["food_name"] + STANDARD_NUTRIENT_COLUMNS + DISEASE_COLUMNS:
        cx, cy = f"{c}_x", f"{c}_y"
        if cx in merged.columns and cy in merged.columns:
            merged[c] = merged[cx].fillna(merged[cy])
            merged = merged.drop(columns=[cx, cy], errors="ignore")
        elif cx in merged.columns:
            merged[c] = merged[cx]
            merged = merged.drop(columns=[cx], errors="ignore")
        elif cy in merged.columns:
            merged[c] = merged[cy]
            merged = merged.drop(columns=[cy], errors="ignore")
    # Combine source_datasets as semicolon-separated (e.g. "usda;meals")
    if "source_datasets_x" in merged.columns and "source_datasets_y" in merged.columns:
        s = merged["source_datasets_x"].fillna("").astype(str) + ";" + merged["source_datasets_y"].fillna("").astype(str)
        merged["source_datasets"] = s.str.strip(";").str.replace(";;", ";", regex=False)
        merged = merged.drop(columns=["source_datasets_x", "source_datasets_y"], errors="ignore")
    return merged


def _merge_frames(frames: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Outer merge on food_name_normalized. For nutrients and disease columns,
    take first non-null across sources (priority: order of frames).
    """
    if not frames:
        return pd.DataFrame()
    merged = frames[0]
    for i in range(1, len(frames)):
        merged = _merge_two(merged, frames[i])
    return merged


def _build_unified_table(
    usda_df: pd.DataFrame,
    meals_df: pd.DataFrame,
    disease_df: pd.DataFrame,
    diet_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build single unified DataFrame from all cleaned sources."""
    frames: List[pd.DataFrame] = []
    if not usda_df.empty:
        usda_df = _select_and_tag(
            ensure_standard_nutrient_columns(usda_df),
            "usda",
            STANDARD_NUTRIENT_COLUMNS,
            DISEASE_COLUMNS,
        )
        frames.append(usda_df)
    if not meals_df.empty:
        meals_df = _select_and_tag(
            ensure_standard_nutrient_columns(meals_df),
            "meals",
            STANDARD_NUTRIENT_COLUMNS,
            DISEASE_COLUMNS,
        )
        frames.append(meals_df)
    if not disease_df.empty:
        disease_df = _select_and_tag(
            _ensure_columns(disease_df, STANDARD_NUTRIENT_COLUMNS + DISEASE_COLUMNS),
            "disease",
            STANDARD_NUTRIENT_COLUMNS,
            DISEASE_COLUMNS,
        )
        frames.append(disease_df)
    if not diet_df.empty:
        diet_df = _select_and_tag(
            _ensure_columns(diet_df, STANDARD_NUTRIENT_COLUMNS + DISEASE_COLUMNS),
            "diet_recommendation",
            STANDARD_NUTRIENT_COLUMNS,
            DISEASE_COLUMNS,
        )
        frames.append(diet_df)

    if not frames:
        return pd.DataFrame(columns=UNIFIED_COLUMNS)

    unified = _merge_frames(frames)
    # Enforce column order
    for c in UNIFIED_COLUMNS:
        if c not in unified.columns:
            unified[c] = float("nan")
    unified = unified[[c for c in UNIFIED_COLUMNS if c in unified.columns]]
    return unified


def run_pipeline(
    usda_dir: Optional[Path] = None,
    meals_file: Optional[str] = None,
    disease_file: Optional[str] = None,
    diet_file: Optional[str] = None,
    output_dir: Optional[Path] = None,
    output_filename: str = "unified_food_features.csv",
) -> pd.DataFrame:
    """
    Run full preprocessing: load and clean each dataset, merge, write unified table.

    Returns:
        Unified DataFrame. Also writes CSV to output_dir / output_filename.
    """
    ensure_processed_dir()
    out_dir = output_dir or PROCESSED_DIR
    out_path = Path(out_dir) / output_filename

    usda = USDAProcessor(base_dir=usda_dir)
    usda_df = usda.run()

    meals = MealsProcessor(file_path=meals_file)
    meals_df = meals.run()

    disease = DiseaseProcessor(file_path=disease_file)
    disease_df = disease.run()

    diet = DietRecommendationProcessor(file_path=diet_file)
    diet_df = diet.run()

    unified = _build_unified_table(usda_df, meals_df, disease_df, diet_df)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    unified.to_csv(out_path, index=False, encoding="utf-8")

    return unified
