# AI Food Nutrition & Disease Risk Prediction Chatbot

## 📌 Project Overview

This project aims to develop an AI-powered mobile application that analyzes food images and food label data to provide:

- Nutritional value breakdown
- Disease suitability prediction
- Personalized diet recommendations
- Sensor-based lifestyle adjustments
- Interactive chatbot support

The application integrates Machine Learning, Computer Vision, and Mobile Development technologies.

---

## 🎯 Project Objectives

1. Automatically detect food items from images.
2. Provide accurate nutrient information.
3. Predict disease risks based on nutrient composition.
4. Suggest healthier dietary alternatives.
5. Personalize recommendations using activity and location sensors.
6. Provide chatbot-based food safety consultation.

---

## 🧱 System Architecture

### Frontend
- Flutter (Dart)
- Camera Integration
- Image Upload
- Sensor Integration
- Chatbot UI
- Result Dashboard

### Backend
- FastAPI (Python)
- REST API
- JSON Response Handling
- CORS Support

### Machine Learning
- TensorFlow CNN for Food Image Classification
- Scikit-Learn Models for Disease Risk Prediction
- Dataset-driven Nutrient Analysis

---

## 📊 Datasets Used

### 1. Food Image Dataset
- Food-101 Dataset
Purpose:
- Train CNN model to detect food from images.

---

### 2. Nutrient Dataset
- USDA FoodData Central Dataset
Purpose:
- Provide macronutrient and micronutrient information.

---

### 3. Disease Suitability Dataset
- Diabetes and Blood Pressure Food Dataset
Purpose:
- Classify food as safe or unsafe for diseases.

---

### 4. Diet Recommendation Dataset
Purpose:
- Suggest alternative healthy foods.

---

### 5. Meal Nutrition Dataset
Purpose:
- Provide complete meal nutrient breakdown.

---

### 6. Human Activity Recognition Dataset
Purpose:
- Detect user activity from accelerometer data.

---

## ⚙️ Core Modules

### Module 1: Food Image Recognition
- Accept food image input
- Preprocess image
- Predict food category using CNN

---

### Module 2: Nutrient Analysis
- Retrieve nutrients from dataset
- Display calorie and nutrient information

---

### Module 3: Disease Risk Prediction
- Predict risk level for:
  - Diabetes
  - Blood Pressure
  - Heart Disease

---

### Module 4: Diet Recommendation Engine
- Suggest healthier alternatives
- Provide dietary advice

---

### Module 5: Sensor-Based Personalization
- Detect physical activity using accelerometer
- Provide location-based dietary suggestions

---

### Module 6: Chatbot System
- Accept user food-related queries
- Provide AI-generated health recommendations

---

## 📁 Project Folder Structure

project-root/
│
├── backend/
│   ├── main.py
│   ├── api/
│   ├── models/
│   └── utils/
│
├── ml_model/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   └── saved_models/
│
├── mobile_app/
│   ├── lib/
│   ├── screens/
│   ├── widgets/
│   └── services/
│
├── datasets/
│
└── documentation/

---

## 🔄 Data Flow

User Uploads Food Image
        ↓
CNN Model Detects Food Name
        ↓
Nutrient Dataset Lookup
        ↓
Disease Risk Prediction Model
        ↓
Diet Recommendation Engine
        ↓
Sensor Personalization Adjustment
        ↓
Results Displayed in Mobile App

---

## 🔌 API Endpoints

POST /predict_food  
Returns nutrient information and disease risk prediction.

POST /chat_query  
Handles chatbot food queries.

POST /sensor_data  
Processes activity and location data.

---

## 🧪 ML Model Workflow

1. Dataset Cleaning and Preprocessing
2. Dataset Merging
3. Feature Selection
4. Model Training
5. Model Evaluation
6. Model Export for Deployment

---

## 📱 Mobile Application Features

- Food Image Capture
- Nutritional Dashboard
- Disease Risk Indicator
- Chatbot Interaction
- Activity Tracking
- Location-based Food Suggestion

---

## 🛠 Development Phases

### Phase 1
Dataset collection and preprocessing

### Phase 2
ML model training and testing

### Phase 3
Backend API development

### Phase 4
Flutter UI development

### Phase 5
Integration and Testing

---

## ✅ Expected Outcomes

- Automated food nutrition analyzer
- Disease-aware diet recommendation system
- Sensor-personalized health assistant
- Fully functional AI mobile application

---

## 🚀 Future Enhancements

- Portion size estimation from images
- Multi-language chatbot support
- Real-time wearable device integration
- Cloud model deployment
