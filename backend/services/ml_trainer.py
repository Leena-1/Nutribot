import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from backend.core.data_loader import data_loader

def train_model():
    print("Starting ML Model training...")
    
    # 1. Load dataset
    df = data_loader.get_nutribot_df()
    if df is None:
        print("Error: nutribot_dataset.xlsx not loaded.")
        return

    # 2. Preprocessing
    # Map Activity Level
    activity_map = {
        "Sedentary": 0,
        "Lightly Active": 0,
        "Low": 0,
        "Moderately Active": 1,
        "Moderate": 1,
        "Very Active": 2,
        "High": 2
    }
    
    # Detect the correct column name for Activity Level
    act_col = 'Activity_Level' if 'Activity_Level' in df.columns else 'Activity Level'
    if act_col not in df.columns:
        print(f"Error: Activity Level column not found. Available: {df.columns.tolist()}")
        return
        
    df['Activity_Level_Encoded'] = df[act_col].map(activity_map).fillna(0).astype(int)
    
    # Fill NaN in Medical Condition
    med_col = 'Medical_Condition' if 'Medical_Condition' in df.columns else 'Medical Condition'
    if med_col in df.columns:
        df[med_col] = df[med_col].fillna('Healthy')

    # 3. Define Features and Target
    # Features (X) - Using underscores as verified in nutribot_dataset.xlsx
    feature_cols = [
        'BMI', 'Activity_Level_Encoded', 'Calorie_Target', 'Calories_Consumed',
        'Protein_Consumed', 'Carbs_Consumed', 'Fat_Consumed', 'Sugar_Consumed',
        'Sodium_Consumed', 'Sodium_Limit'
    ]
    
    # Final check and fallback support for spaces
    final_features = []
    for col in feature_cols:
        if col in df.columns or col == 'Activity_Level_Encoded':
            final_features.append(col)
        else:
            space_col = col.replace('_', ' ')
            if space_col in df.columns:
                final_features.append(space_col)
            else:
                print(f"Error: Column {col} (or {space_col}) not found in dataset.")
                return

    X = df[final_features]
    
    # Target (y)
    target_col = 'Risk_Label' if 'Risk_Label' in df.columns else 'Risk Label'
    y = df[target_col]

    # 4. Split and Train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Training Accuracy: {accuracy_score(y_train, model.predict(X_train)):.4f}")
    print(f"Test Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    if acc < 0.75:
        print("Warning: Test accuracy is below 0.75, but saving model anyway.")
    
    # Save Model
    model_path = "backend/models/risk_model.pkl"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
