# Dataset Preprocessing Pipeline (Step 1)

This module cleans and merges the project datasets and produces a **unified food feature table** used by the ML models and API.

## What it does

1. **Loads** CSV data from:
   - USDA FoodData Central (`datasets/usda/`)
   - Nutrition Daily Meals (`datasets/meals/`)
   - Diabetes and Blood Pressure Food (`datasets/disease/`)
   - Diet Recommendation (`datasets/diet_recommendation/`)

2. **Cleans** each dataset:
   - Normalizes food names for merging
   - Maps nutrient columns to standard names and units (e.g. `energy_kcal`, `protein_g`, `sodium_mg`)
   - Converts disease suitability to 0/1 where applicable

3. **Merges** all sources on `food_name_normalized` (outer join).

4. **Writes** `datasets/processed/unified_food_features.csv` with columns:
   - `food_name`, `food_name_normalized`, `source_datasets`
   - Standard nutrients: `energy_kcal`, `protein_g`, `total_fat_g`, `carbohydrates_g`, `fiber_g`, `sugars_g`, `sodium_mg`, `potassium_mg`, `calcium_mg`, `iron_mg`, `vitamin_a_iu`, `vitamin_c_mg`, `cholesterol_mg`, `saturated_fat_g`
   - Disease: `suitable_diabetes`, `suitable_blood_pressure`, `suitable_heart`
   - Diet: `diet_type`, `recommendation_notes`

## Installation

From project root:

```bash
pip install -r requirements.txt
```

## Running the pipeline

From project root:

```bash
python -m ml_model.preprocessing.run_preprocessing
```

If no dataset files are present, the script still runs and writes an empty table; add CSVs as described in `datasets/README.md`.

## Configuring column names

If your CSV headers differ, edit `ml_model/preprocessing/config.py`:

- `USDA_COLUMN_MAP` – USDA food/nutrient file column names and nutrient IDs
- `MEALS_COLUMN_MAP` – meal dataset food name and nutrient column names
- `DISEASE_COLUMN_MAP` – disease dataset food name and suitability columns
- `DIET_COLUMN_MAP` – diet recommendation food name and diet/notes columns

## Testing without real datasets

You can create small CSVs under each `datasets/<source>/` folder with the expected columns (see `datasets/README.md`). The pipeline will merge them and produce `unified_food_features.csv`. For a quick test, use `create_sample_datasets.py` to generate sample files.
