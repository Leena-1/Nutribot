"""
Diet Recommendation dataset processor.

Expects a CSV with food name and columns for diet type / recommendation notes.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from ml_model.preprocessing.base_processor import BaseDatasetProcessor
from ml_model.preprocessing.config import DIET_DIR, DIET_COLUMN_MAP, get_diet_recommendation_paths
from ml_model.preprocessing.utils import find_column, normalize_food_name


class DietRecommendationProcessor(BaseDatasetProcessor):
    """Load and clean diet recommendation dataset."""

    def __init__(self, file_path: Optional[str] = None):
        path = file_path or get_diet_recommendation_paths()["diet_file"]
        if not Path(path).exists():
            path = get_diet_recommendation_paths().get("diet_dataset_file", path)
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
        name_col = find_column(DIET_COLUMN_MAP["food_name"], out.columns.tolist())
        if not name_col:
            name_col = out.columns[0]
        out = out.rename(columns={name_col: "food_name"})

        diet_col = find_column(DIET_COLUMN_MAP["diet_type"], out.columns.tolist())
        if diet_col:
            out["diet_type"] = out[diet_col].astype(str)
        else:
            out["diet_type"] = ""

        rec_col = find_column(DIET_COLUMN_MAP["recommendation_notes"], out.columns.tolist())
        if rec_col:
            out["recommendation_notes"] = out[rec_col].astype(str)
        else:
            out["recommendation_notes"] = ""

        out["food_name_normalized"] = out["food_name"].astype(str).map(normalize_food_name)
        out = out[out["food_name"].notna() & (out["food_name"].astype(str).str.strip() != "")]
        return out
