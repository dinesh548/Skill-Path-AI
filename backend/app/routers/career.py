from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.career_pathway import CareerPathwayEngine

router = APIRouter(prefix="/career-pathways", tags=["Career Pathways"])

@router.get("/{employee_id}")
def get_employee_career_pathway(
    employee_id: str,
    target_role_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    engine = CareerPathwayEngine(db)
    result = engine.get_career_pathway(employee_id, target_role_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
