"""
Nutrition Daily Meals dataset processor.

Expects a CSV with food/meal name and nutrient columns. Column names
are matched flexibly via MEALS_COLUMN_MAP.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from ml_model.preprocessing.base_processor import BaseDatasetProcessor
from ml_model.preprocessing.config import MEALS_DIR, MEALS_COLUMN_MAP, get_meals_paths
from ml_model.preprocessing.utils import (
    find_column,
    normalize_food_name,
    map_nutrient_columns,
    ensure_standard_nutrient_columns,
)
from ml_model.preprocessing.constants import STANDARD_NUTRIENT_COLUMNS


class MealsProcessor(BaseDatasetProcessor):
    """Load and clean Nutrition Daily Meals (or similar) CSV into standard nutrient columns."""

    def __init__(self, file_path: Optional[str] = None):
        path = file_path or get_meals_paths()["meals_file"]
        # If default path doesn't exist, try alternative
        if not Path(path).exists():
            alt = get_meals_paths().get("daily_nutrition_file")
            if alt and Path(alt).exists():
                path = alt
        super().__init__(path)

    def load(self) -> pd.DataFrame:
        if not self.file_path.exists():
            return pd.DataFrame()
        self.raw_df = pd.read_csv(
            self.file_path, encoding="utf-8", on_bad_lines="skip", low_memory=False
        )
        return self.raw_df

    def clean(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        df = df if df is not None else self.raw_df
        if df is None or df.empty:
            return pd.DataFrame()

        out = df.copy()
        # Resolve food name column
        name_col = find_column(MEALS_COLUMN_MAP["food_name"], out.columns.tolist())
        if not name_col:
            name_col = out.columns[0]
        out = out.rename(columns={name_col: "food_name"})

        # Map nutrient columns: try config first, then generic alias map
        for canonical, candidates in [
            ("energy_kcal", MEALS_COLUMN_MAP["energy_kcal"]),
            ("protein_g", MEALS_COLUMN_MAP["protein_g"]),
            ("total_fat_g", MEALS_COLUMN_MAP["total_fat_g"]),
            ("carbohydrates_g", MEALS_COLUMN_MAP["carbohydrates_g"]),
            ("fiber_g", MEALS_COLUMN_MAP["fiber_g"]),
            ("sugars_g", MEALS_COLUMN_MAP["sugars_g"]),
            ("sodium_mg", MEALS_COLUMN_MAP["sodium_mg"]),
        ]:
            src = find_column(candidates, out.columns.tolist())
            if src and canonical not in out.columns:
                out[canonical] = pd.to_numeric(out[src], errors="coerce")

        # Any remaining nutrient-like columns via alias map
        mapped = map_nutrient_columns(out)
        for c in STANDARD_NUTRIENT_COLUMNS:
            if c in mapped.columns and (c not in out.columns or out[c].isna().all()):
                out[c] = mapped[c]

        out = ensure_standard_nutrient_columns(out)
        out["food_name_normalized"] = out["food_name"].astype(str).map(normalize_food_name)
        out = out[out["food_name"].notna() & (out["food_name"].astype(str).str.strip() != "")]
        return out
