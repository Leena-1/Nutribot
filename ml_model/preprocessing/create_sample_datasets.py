"""
Create minimal sample CSV files under datasets/ for testing the preprocessing pipeline.

Run from project root:
    python -m ml_model.preprocessing.create_sample_datasets
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
else:
    project_root = Path(__file__).resolve().parents[2]

from ml_model.preprocessing.config import USDA_DIR, MEALS_DIR, DISEASE_DIR, DIET_DIR


def main():
    base = project_root / "datasets"
    base.mkdir(parents=True, exist_ok=True)

    # 1) USDA-style single file (food + nutrients)
    usda_dir = base / "usda"
    usda_dir.mkdir(parents=True, exist_ok=True)
    usda_csv = usda_dir / "food_nutrients.csv"
    usda_content = """description,Energy,Protein,Total lipid (fat),Carbohydrate,Fiber,Sugars,Sodium,Potassium,Calcium,Iron,Vitamin A,Vitamin C,Cholesterol
Butter,717,0.85,81.11,0.06,0,0.06,11,24,24,0.02,2499,0,0.17
Broccoli,34,2.82,0.37,6.64,2.6,1.7,33,316,47,0.73,623,89.2,0
Chicken breast,165,31.02,3.6,0,0,0,74,256,15,0.37,0,0,0.73
"""
    usda_csv.write_text(usda_content, encoding="utf-8")
    print("Created", usda_csv)

    # 2) Meals
    meals_dir = base / "meals"
    meals_dir.mkdir(parents=True, exist_ok=True)
    meals_csv = meals_dir / "meals.csv"
    meals_content = """Food,Calories,Protein (g),Total Fat (g),Carbohydrates (g),Fiber (g),Sodium (mg)
Oatmeal,150,5,3,27,4,0
Apple,95,0.5,0.3,25,4,2
"""
    meals_csv.write_text(meals_content, encoding="utf-8")
    print("Created", meals_csv)

    # 3) Disease suitability
    disease_dir = base / "disease"
    disease_dir.mkdir(parents=True, exist_ok=True)
    disease_csv = disease_dir / "food_disease.csv"
    disease_content = """Food,Diabetes,Blood pressure,Heart
Broccoli,1,1,1
Butter,0,0,0
Chicken breast,1,1,1
Oatmeal,1,1,1
"""
    disease_csv.write_text(disease_content, encoding="utf-8")
    print("Created", disease_csv)

    # 4) Diet recommendation
    diet_dir = base / "diet_recommendation"
    diet_dir.mkdir(parents=True, exist_ok=True)
    diet_csv = diet_dir / "diet_recommendation.csv"
    diet_content = """Food,Diet,Recommendation
Broccoli,Vegan,High fiber; good for heart
Oatmeal,Vegan,Good for diabetes and BP
"""
    diet_csv.write_text(diet_content, encoding="utf-8")
    print("Created", diet_csv)
    print("Done. Run: python -m ml_model.preprocessing.run_preprocessing")


if __name__ == "__main__":
    main()
