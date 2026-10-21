from fastapi import APIRouter
from app.schemas.recommend import StudentProfile, RecommendationResponse
from app.services.recommender import get_recommendations

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.post("/", response_model=RecommendationResponse)
def recommend(profile: StudentProfile):
    return {"recommendations": get_recommendations(profile)}