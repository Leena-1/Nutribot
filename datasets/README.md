# Datasets Directory

Place your dataset files here as described below. The preprocessing pipeline expects these paths (configurable in `ml_model/preprocessing/config.py`).

## Required Datasets

### 1. USDA FoodData Central
- **Source:** https://fdc.nal.usda.gov/download-datasets
- **Suggested:** SR Legacy or Foundation Foods (CSV)
- **Place in:** `datasets/usda/`
- **Expected files (SR Legacy style):**
  - `food.csv` – food descriptions, FDC IDs
  - `food_nutrient.csv` – food_id, nutrient_id, amount
  - `nutrient.csv` – nutrient_id, name, unit_name
- **Alternative:** Single CSV with columns: `fdc_id` or `description`, plus nutrient columns (e.g. `Energy`, `Protein`, `Total lipid (fat)`)

## 📊 Nutribot Dataset Inventory (Current: 7)
The system leverages 7 specialized datasets for nutrition analysis and health risk assessment:

1. **Exercise_Recommendation_Dataset.xlsx**: Mapping of activities to calorie burn.
2. **Food_Safety_ML_Dataset.xlsx**: Safety & risk assessment for food items.
3. **nutribot_dataset.xlsx**: (New) User-specific dietary patterns for personalization.
4. **Updated_Indian_Food_Nutrition_Dataset.xlsx**: (New) 1000+ Indian dishes with calories, macros, GI, and sodium.
5. **User_Daily_Intake.csv**: User meal consumption history for trend analysis.
6. **food_mapping.json**: AI category mapping for food recognition & categorization.
7. **feature_names.json**: ML model features for risk & disease prediction.

### 3. Diabetes and Blood Pressure Food Dataset
- **Source:** Kaggle or similar (food-level disease suitability)
- **Place in:** `datasets/disease/`
- **Expected:** CSV with food name/item and columns indicating suitability for diabetes, blood pressure, heart (e.g. `diabetes_safe`, `bp_safe`, or similar)

### 4. Diet Recommendation Dataset
- **Source:** Kaggle "Diet Recommendation" or similar
- **Place in:** `datasets/diet_recommendation/`
- **Expected:** CSV with food names and recommendation/alternative/health labels

### 5. Food-101 (for Step 2 – image model)
- **Place in:** `datasets/food101/` when needed for CNN training

## After Adding Datasets

Run the preprocessing pipeline from project root:

```bash
python -m ml_model.preprocessing.run_preprocessing
```

Output: `datasets/processed/unified_food_features.csv` (and optional intermediate artifacts).
