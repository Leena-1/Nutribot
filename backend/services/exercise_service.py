import pandas as pd
from typing import List, Dict, Any
import os

class ExerciseService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.exercise_df = None
        self.lookup_df = None
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            print(f"WARNING: Exercise dataset not found at {self.file_path}")
            return
        
        try:
            # Load sheets
            self.exercise_df = pd.read_excel(self.file_path, sheet_name="Exercise Dataset")
            self.lookup_df = pd.read_excel(self.file_path, sheet_name="Recommendation Lookup")
            print("Exercise Dataset loaded successfully.")
        except Exception as e:
            print(f"ERROR loading Exercise Dataset: {e}")

    def recommend_exercises(self, bmi_group: str, activity_level: str, medical_condition: str = None) -> List[Dict[str, Any]]:
        if self.exercise_df is None:
            return []

        # 1. Filter by BMI Group (e.g., 'Normal', 'Overweight')
        filtered = self.exercise_df[self.exercise_df['BMI Group'].str.contains(bmi_group, case=False, na=False)]
        
        # 2. Filter by Activity Level (e.g., 'Sedentary', 'Lightly Active')
        filtered = filtered[filtered['Suitable Activity Levels'].str.contains(activity_level, case=False, na=False)]
        
        # 3. Filter out medical cautions
        if medical_condition and medical_condition.lower() != "none":
            # Exclude if Medical Caution matches user condition
            filtered = filtered[~filtered['Medical Caution'].str.contains(medical_condition, case=False, na=False)]
            
        # 4. Sort by Calories Burned (kcal) descending
        top_3 = filtered.sort_values(by='Calories Burned (kcal)', ascending=False).head(3)
        
        results = []
        for _, row in top_3.iterrows():
            results.append({
                "name": str(row['Exercise Name']),
                "duration": int(row['Duration (min)']),
                "calories_burned": float(row['Calories Burned (kcal)']),
                "category": str(row['Category']),
                "intensity": str(row['Intensity Level'])
            })
            
        return results

# Initialize singleton
# Note: Path is relative to backend execution (usually root)
DATASET_PATH = os.path.join("datasets", "Exercise_Recommendation_Dataset.xlsx")
exercise_service = ExerciseService(DATASET_PATH)
