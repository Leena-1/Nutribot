import os
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_KEY = BASE_DIR / "firebase-key.json"

# Initialize Firebase safely
if not firebase_admin._apps:
    if os.path.exists(SERVICE_ACCOUNT_KEY):
        cred = credentials.Certificate(str(SERVICE_ACCOUNT_KEY))
        firebase_admin.initialize_app(cred)
    else:
        # Fallback for development if file is missing (will error on access)
        print(f"WARNING: Firebase service account key not found at {SERVICE_ACCOUNT_KEY}")

db = firestore.client()

# Collections
users_collection = db.collection("users")
meals_collection = db.collection("meals")
