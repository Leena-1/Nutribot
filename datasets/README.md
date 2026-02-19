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

### 2. Nutrition Daily Meals Dataset
- **Source:** e.g. Kaggle "Daily Food & Nutrition Dataset" or similar
- **Place in:** `datasets/meals/`
- **Expected:** CSV with meal/food name and nutrient columns (calories, protein, carbs, fat, etc.)

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
