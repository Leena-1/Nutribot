from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.database import users_collection
from backend.services.exercise_service import exercise_service

router = APIRouter()

class ExerciseRecommendationRequest(BaseModel):
    user_id: str

@router.post("/recommend-exercise")
async def recommend_exercise(request: ExerciseRecommendationRequest):
    try:
        # Fetch user data from Firestore
        user_doc = users_collection.document(request.user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
            
        user_data = user_doc.to_dict()
        
        # Get user attributes for filtering
        activity_level = user_data.get("activity_level", "Sedentary")
        medical_condition = user_data.get("medical_condition", "None") or "None"
        bmi_group = user_data.get("bmi_group", "Normal")
        
        # Call the recommendation service
        exercises = exercise_service.recommend_exercises(
            bmi_group=bmi_group,
            activity_level=activity_level,
            medical_condition=medical_condition
        )
        
        return {
            "status": "success",
            "user_context": {
                "activity_level": activity_level,
                "bmi_group": bmi_group,
                "medical_condition": medical_condition
            },
            "recommendations": exercises
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recommend exercises: {str(e)}")
