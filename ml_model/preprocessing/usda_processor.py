"""
USDA FoodData Central dataset processor.

Supports:
1. Multi-file format: food.csv, food_nutrient.csv, nutrient.csv (SR Legacy style)
2. Single-file format: one CSV with food description + nutrient columns
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from ml_model.preprocessing.base_processor import BaseDatasetProcessor
from ml_model.preprocessing.config import USDA_DIR, USDA_COLUMN_MAP, get_usda_paths
from ml_model.preprocessing.utils import normalize_food_name, map_nutrient_columns, ensure_standard_nutrient_columns


class USDAProcessor(BaseDatasetProcessor):
    """Load and clean USDA FoodData Central data into a flat table with standard nutrient columns."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else USDA_DIR
        self.paths = get_usda_paths() if not base_dir else {
            "food_file": str(self.base_dir / "food.csv"),
            "food_nutrient_file": str(self.base_dir / "food_nutrient.csv"),
            "nutrient_file": str(self.base_dir / "nutrient.csv"),
            "single_food_nutrients_file": str(self.base_dir / "food_nutrients.csv"),
        }
        super().__init__(self.paths["food_file"])

    def load(self) -> pd.DataFrame:
        """Try single-file first, then multi-file (food + food_nutrient + nutrient)."""
        single = self.base_dir / "food_nutrients.csv"
        if single.exists():
            self.raw_df = pd.read_csv(single, encoding="utf-8", on_bad_lines="skip", low_memory=False)
            return self.raw_df

        food_path = self.base_dir / "food.csv"
        fn_path = self.base_dir / "food_nutrient.csv"
        nut_path = self.base_dir / "nutrient.csv"

        if not food_path.exists():
            return pd.DataFrame()

        food = pd.read_csv(food_path, encoding="utf-8", on_bad_lines="skip", low_memory=False)
        cm = USDA_COLUMN_MAP
        fid = cm["food"]["id"]
        fname = cm["food"]["name"]
        if fid not in food.columns:
            fid = "fdc_id" if "fdc_id" in food.columns else food.columns[0]
        if fname not in food.columns:
            for c in ["description", "long_description", "food_name"]:
                if c in food.columns:
                    fname = c
                    break

        # If we have food_nutrient and nutrient, pivot to wide
        if fn_path.exists() and nut_path.exists():
            fn = pd.read_csv(fn_path, encoding="utf-8", on_bad_lines="skip", low_memory=False)
            nut = pd.read_csv(nut_path, encoding="utf-8", on_bad_lines="skip", low_memory=False)
            id_to_canonical = cm["nutrient_id_to_canonical"]
            fn = fn.merge(nut[["id", "name"]], left_on="nutrient_id", right_on="id", how="left")
            fn["canonical"] = fn["nutrient_id"].map(id_to_canonical)
            fn = fn.dropna(subset=["canonical"])
            wide = fn.pivot_table(index="fdc_id", columns="canonical", values="amount", aggfunc="first")
            food = food.merge(wide, left_on=fid, right_index=True, how="left")
            food = food.rename(columns={fname: "description"})
        else:
            # Only food.csv: try to map existing columns to nutrients
            if fname in food.columns:
                food = food.rename(columns={fname: "description"})
            mapped = map_nutrient_columns(food)
            for c in mapped.columns:
                if c not in food.columns:
                    food[c] = mapped[c]

        food["food_name_normalized"] = food["description"].astype(str).map(normalize_food_name)
        self.raw_df = food
        return self.raw_df

    def clean(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        df = df if df is not None else self.raw_df
        if df is None or df.empty:
            return pd.DataFrame()

        out = df.copy()
        if "description" not in out.columns and "food_name" not in out.columns:
            for c in ["description", "long_description", "food_name"]:
                if c in out.columns:
                    out = out.rename(columns={c: "food_name"})
                    break
        if "food_name" not in out.columns and "description" in out.columns:
            out["food_name"] = out["description"]

        out = ensure_standard_nutrient_columns(out)
        # Drop rows with no usable name
        name_col = "food_name" if "food_name" in out.columns else "description"
        out = out[out[name_col].notna() & (out[name_col].astype(str).str.strip() != "")]
        return out
