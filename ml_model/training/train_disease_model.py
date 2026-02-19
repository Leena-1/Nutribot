"""
Train disease prediction models from unified_food_features.csv.

Run after Step 1 preprocessing:
  python -m ml_model.training.train_disease_model
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_model.training.disease_model import load_unified_data, train_disease_models, UNIFIED_CSV


def main() -> int:
    if not UNIFIED_CSV.exists():
        print("Run preprocessing first: python -m ml_model.preprocessing.run_preprocessing")
        return 1
    df = load_unified_data()
    if df.empty:
        print("Unified CSV is empty. Add datasets and re-run preprocessing.")
        return 1
    results = train_disease_models(df)
    if not results:
        print("No targets with enough variation to train. Add disease/diet data and re-run.")
        return 1
    for target, meta in results.items():
        print(f"  {target}: accuracy = {meta.get('accuracy', 0):.4f}")
    print("Models saved to ml_model/saved_models/disease_model/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
