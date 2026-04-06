import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    _instance = None
    _food_safety_df = None
    _nutribot_df = None
    _indian_food_df = None
    _exercise_df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        base_path = "backend/data"
        
        files = {
            "Food_Safety_ML_Dataset.xlsx": "Food_Safety_Dataset",
            "nutribot_dataset.xlsx": "Sheet1",
            "Updated_Indian_Food_Nutrition_Dataset.xlsx": "Sheet1",
            "Exercise_Recommendation_Dataset.xlsx": "Exercise Dataset"
        }

        for filename, sheet in files.items():
            path = os.path.join(base_path, filename)
            if not os.path.exists(path):
                logger.error(f"File not found: {path}")
                continue
            
            try:
                df = pd.read_excel(path, sheet_name=sheet)
                
                # Strip whitespace from column names
                df.columns = [c.strip() for c in df.columns]
                
                # Strip whitespace from string values
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                
                # Fill NaN in Medical_Condition (or similar) with "Healthy"
                # Note: Different datasets might have different column names for medical condition
                if "Medical Condition" in df.columns:
                    df["Medical Condition"] = df["Medical Condition"].fillna("Healthy")
                if "Medical_Condition" in df.columns:
                    df["Medical_Condition"] = df["Medical_Condition"].fillna("Healthy")
                
                if filename == "Food_Safety_ML_Dataset.xlsx":
                    self._food_safety_df = df
                elif filename == "nutribot_dataset.xlsx":
                    self._nutribot_df = df
                elif filename == "Updated_Indian_Food_Nutrition_Dataset.xlsx":
                    self._indian_food_df = df
                    print(f"Food columns: {list(df.columns)}")
                elif filename == "Exercise_Recommendation_Dataset.xlsx":
                    self._exercise_df = df
                
                print(f"Loaded {filename}: {len(df)} rows")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")

    def get_food_safety_df(self):
        return self._food_safety_df

    def get_nutribot_df(self):
        return self._nutribot_df

    def get_indian_food_df(self):
        return self._indian_food_df

    def get_exercise_df(self):
        return self._exercise_df

# Global instance
data_loader = DataLoader()
