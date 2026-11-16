from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import schemas
from backend.app.services.recommendation import CourseRecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{employee_id}")
def get_recommendations_for_employee(
    employee_id: str,
    planning_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    engine = CourseRecommendationEngine(db)
    result = engine.generate_recommendations(employee_id, planning_date)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/generate")
def generate_recommendations(
    payload: schemas.RecommendationGenerateRequest,
    db: Session = Depends(get_db)
):
    engine = CourseRecommendationEngine(db)
    result = engine.generate_recommendations(payload.employee_id, payload.planning_date)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
