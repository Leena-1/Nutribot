"""
Base class for dataset processors. Each dataset type has a processor
that loads, cleans, and returns a DataFrame with standardized columns where possible.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

from ml_model.preprocessing.utils import normalize_food_name, find_column


class BaseDatasetProcessor(ABC):
    """Load and clean a single dataset; output should include food identifier and any nutrients/disease flags."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.raw_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        """Load CSV (or override for JSON)."""
        if not self.file_path.exists():
            return pd.DataFrame()
        self.raw_df = pd.read_csv(self.file_path, encoding="utf-8", on_bad_lines="skip", low_memory=False)
        return self.raw_df

    @abstractmethod
    def clean(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Clean and standardize columns. If df is None, use self.raw_df."""
        pass

    def get_food_name_column(self, df: pd.DataFrame, candidates: list) -> Optional[str]:
        """Helper: resolve food name column from candidates."""
        return find_column(candidates, df.columns.tolist())

    def add_normalized_name(self, df: pd.DataFrame, name_col: str) -> pd.DataFrame:
        """Add food_name_normalized for merging."""
        df = df.copy()
        df["food_name_normalized"] = df[name_col].astype(str).map(normalize_food_name)
        return df

    def run(self) -> pd.DataFrame:
        """Load and clean; return cleaned DataFrame."""
        df = self.load()
        if df.empty:
            return df
        self.cleaned_df = self.clean(df)
        return self.cleaned_df
