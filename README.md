# Nutribot – AI Food Nutrition & Disease Risk Prediction

Full-stack mobile app: food image analysis, nutrient lookup, disease suitability, diet recommendations, and chatbot.

## Project structure

```
Nutribot/
├── backend/          # FastAPI (predict_food, chat_query)
├── ml_model/         # Preprocessing, CNN training, disease models
├── mobile_app/       # Flutter app (scan, results, chat)
├── datasets/         # Raw and processed data
└── requirements.txt
```

## Quick start

### 1. Preprocessing (Step 1)

```bash
pip install -r requirements.txt
python -m ml_model.preprocessing.create_sample_datasets   # optional sample data
python -m ml_model.preprocessing.run_preprocessing
```

Output: `datasets/processed/unified_food_features.csv`

### 2. Train disease model (Step 3)

```bash
python -m ml_model.training.train_disease_model
```

Models saved to `ml_model/saved_models/disease_model/`

### 3. (Optional) Train food CNN (Step 2)

Download [Food-101](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) and extract so that `datasets/food101/images/` has one subfolder per class (e.g. `apple_pie/`, `bread_pudding/`). Then:

```bash
python -m ml_model.training.train_food_cnn --epochs 5 --batch_size 32
```

### 4. Run backend

```bash
cd Nutribot
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 5. Run Flutter app

Ensure Flutter SDK is installed. If `mobile_app` does not yet have full Android/iOS project files, generate them (from repo root):

```bash
cd mobile_app
flutter create . --project-name nutribot
```

Then install and run:

```bash
flutter pub get
flutter run
```

- **Android emulator:** API base URL is set to `http://10.0.2.2:8000` (host machine).
- **iOS simulator / device:** Change base URL in `lib/services/api_service.dart` if needed (e.g. your machine’s IP).

## Testing

- **Backend:** `GET /health`; use `/docs` to try `POST /api/predict_food`, `/api/chat_query`.
- **Preprocessing:** After `run_preprocessing`, check `datasets/processed/unified_food_features.csv`.
- **Disease model:** After `train_disease_model`, call `predict_disease()` from `ml_model.training.disease_model` with a nutrient dict.

## Sensors (removed)

The original design included a sensor module (accelerometer + GPS with a `/api/sensor_data` endpoint), but this has been removed in the current version to keep the app focused on image analysis, nutrient lookup, disease suitability, diet recommendations, and chatbot.
