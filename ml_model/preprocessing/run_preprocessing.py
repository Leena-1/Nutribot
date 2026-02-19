"""
Entry point for the dataset preprocessing pipeline.

Run from project root:
    python -m ml_model.preprocessing.run_preprocessing

Or:
    cd ml_model/preprocessing && python run_preprocessing.py
"""

import sys
from pathlib import Path

# Allow running as script from preprocessing dir or from project root
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from ml_model.preprocessing.merge_pipeline import run_pipeline
from ml_model.preprocessing.config import PROCESSED_DIR


def main() -> int:
    print("Running dataset preprocessing pipeline...")
    unified = run_pipeline()
    if unified.empty:
        print("No data was loaded. Add CSV files under datasets/ (see datasets/README.md).")
        print("Output:", PROCESSED_DIR / "unified_food_features.csv")
        return 0
    print(f"Unified table: {len(unified)} rows, {len(unified.columns)} columns")
    print(f"Output written to: {PROCESSED_DIR / 'unified_food_features.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
