"""
Diabetes and Blood Pressure Food dataset processor.

Expects a CSV with food name and columns indicating suitability for
diabetes, blood pressure, and/or heart disease. Values can be binary (0/1, Y/N)
or text (e.g. "Good", "Bad"); normalized to 0/1 for suitability.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from ml_model.preprocessing.base_processor import BaseDatasetProcessor
from ml_model.preprocessing.config import DISEASE_DIR, DISEASE_COLUMN_MAP, get_disease_paths
from ml_model.preprocessing.utils import find_column, normalize_food_name


def _to_suitable(series: pd.Series) -> pd.Series:
    """Convert various encodings to 0/1 (1 = suitable/safe)."""
    def one_val(x):
        if pd.isna(x):
            return None
        s = str(x).strip().lower()
        if s in ("1", "true", "yes", "y", "good", "safe", "suitable", "recommended"):
            return 1
        if s in ("0", "false", "no", "n", "bad", "unsafe", "avoid"):
            return 0
        try:
            return 1 if float(x) > 0 else 0
        except (TypeError, ValueError):
            return None
    return series.map(one_val)


class DiseaseProcessor(BaseDatasetProcessor):
    """Load and clean disease suitability dataset."""

    def __init__(self, file_path: Optional[str] = None):
        path = file_path or get_disease_paths()["food_disease_file"]
        if not Path(path).exists():
            path = get_disease_paths().get("diabetes_bp_foods_file", path)
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
        name_col = find_column(DISEASE_COLUMN_MAP["food_name"], out.columns.tolist())
        if not name_col:
            name_col = out.columns[0]
        out = out.rename(columns={name_col: "food_name"})

        for canonical, candidates in [
            ("suitable_diabetes", DISEASE_COLUMN_MAP["suitable_diabetes"]),
            ("suitable_blood_pressure", DISEASE_COLUMN_MAP["suitable_blood_pressure"]),
            ("suitable_heart", DISEASE_COLUMN_MAP["suitable_heart"]),
        ]:
            src = find_column(candidates, out.columns.tolist())
            if src:
                out[canonical] = _to_suitable(out[src])
            else:
                out[canonical] = None

        out["food_name_normalized"] = out["food_name"].astype(str).map(normalize_food_name)
        out = out[out["food_name"].notna() & (out["food_name"].astype(str).str.strip() != "")]
        return out
