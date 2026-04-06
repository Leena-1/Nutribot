from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.database import users_collection
from passlib.context import CryptContext

router = APIRouter()

# Password hashing configuration - using sha256_crypt for Windows compatibility
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# ===== SCHEMAS =====
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    age: int
    weight: float
    height: float = 170.0
    gender: str = "Other"
    activity_level: str = "Sedentary"  # Sedentary / Lightly Active / Moderately Active / Very Active
    medical_condition: str = "None"
    diseases: list[str] = []

# ===== HELPERS =====
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ===== SIGNUP =====
@router.post("/signup")
async def signup(user: SignupRequest):
    # Check if user already exists
    # Note: Using get() is blocking, but Firestore also has streaming for lists.
    # For a single check, where().limit(1).get() is usually fine.
    existing = users_collection.where("email", "==", user.email).limit(1).get()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)

    # Calculate BMI group
    bmi = user.weight / ((user.height / 100) ** 2) if user.height else 0
    bmi_group = "Normal"
    if bmi < 18.5: bmi_group = "Underweight"
    elif bmi < 25: bmi_group = "Normal"
    elif bmi < 30: bmi_group = "Overweight"
    else: bmi_group = "Obese"

    new_user_data = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "gender": user.gender,
        "bmi": round(bmi, 2),
        "bmi_group": bmi_group,
        "activity_level": user.activity_level,
        "medical_condition": user.medical_condition,
        "diseases": user.diseases,
        "calorie_limit": 2000,
        "calorie_remaining": 2000
    }

    # Store in Firestore
    _, doc_ref = users_collection.add(new_user_data)

    return {
        "message": "User created successfully",
        "user_id": doc_ref.id
    }

# ===== LOGIN =====
@router.post("/login")
async def login(data: LoginRequest):
    # Fetch user by email
    docs = users_collection.where("email", "==", data.email).limit(1).get()

    if not docs:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_doc = docs[0]
    user_data = user_doc.to_dict()

    # Validate credentials correctly (fix the bug)
    if not verify_password(data.password, user_data.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Success: return all user data (excluding password)
    return {
        "message": "Login successful",
        "user_id": user_doc.id,
        "full_name": user_data.get("full_name"),
        "email": user_data.get("email"),
        "age": user_data.get("age", 0),
        "weight": user_data.get("weight", 0.0),
        "gender": user_data.get("gender", "--"),
        "bmi": user_data.get("bmi", 0.0),
        "bmi_group": user_data.get("bmi_group", "Normal"),
        "activity_level": user_data.get("activity_level", "Sedentary"),
        "medical_condition": user_data.get("medical_condition", "None"),
        "calorie_remaining": user_data.get("calorie_remaining", 2000.0),
        "diseases": user_data.get("diseases", [])
    }
