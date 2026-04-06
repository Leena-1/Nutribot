import sys
import pandas as pd
from pathlib import Path

# Fix path to allow running directly
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml_model.preprocessing.config import PROCESSED_DIR

def run_pipeline() -> pd.DataFrame:
    print("Loading Food_Safety_ML_Dataset.xlsx...")
    dataset_path = project_root / "datasets" / "Food_Safety_ML_Dataset.xlsx"
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        return pd.DataFrame()
    
    df = pd.read_excel(dataset_path)
    
    out_dir = PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "User_Daily_Intake.csv"
    
    df.to_csv(out_path, index=False)
    print(f"Successfully processed dataset to {out_path}")
    return df

def main() -> int:
    print("Running dataset preprocessing pipeline...")
    df = run_pipeline()
    if df.empty:
        return 1
    print(f"Dataset processed: {len(df)} rows, {len(df.columns)} columns")
    return 0

if __name__ == "__main__":
    sys.exit(main())
