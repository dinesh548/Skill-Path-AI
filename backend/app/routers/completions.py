from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.services.tracking_service import TrackingService

router = APIRouter(prefix="/completions", tags=["Completions"])

@router.get("", response_model=List[schemas.CompletionOut])
def get_completions(
    employee_id: Optional[str] = None,
    reassessment_done: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Completion).join(models.Enrollment)
    if employee_id:
        query = query.filter(models.Enrollment.employee_id == employee_id)
    if reassessment_done is not None:
        query = query.filter(models.Completion.reassessment_done == reassessment_done)

    completions = query.order_by(models.Completion.completion_date.desc()).offset(skip).limit(limit).all()
    results = []
    for cmp in completions:
        enr = cmp.enrollment
        results.append({
            "id": cmp.id,
            "enrollment_id": cmp.enrollment_id,
            "employee_id": enr.employee_id if enr else None,
            "employee_name": enr.employee.name if enr and enr.employee else None,
            "course_id": enr.course_id if enr else None,
            "course_title": enr.course.title if enr and enr.course else None,
            "completion_date": cmp.completion_date,
            "assessment_score": float(cmp.assessment_score),
            "reassessment_done": cmp.reassessment_done,
            "previous_proficiency": cmp.previous_proficiency,
            "new_proficiency": cmp.new_proficiency,
            "skill_improvement": cmp.skill_improvement,
            "certificate_url": cmp.certificate_url
        })
    return results

@router.post("", status_code=201)
def record_completion(
    payload: schemas.CompletionCreate,
    db: Session = Depends(get_db)
):
    service = TrackingService(db)
    result = service.complete_course(
        enrollment_id=payload.enrollment_id,
        assessment_score=payload.assessment_score,
        completion_date=payload.completion_date
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to record completion"))
    return result

@router.post("/{completion_id}/reassess")
def trigger_reassessment(
    completion_id: str,
    payload: Optional[schemas.ReassessmentRequest] = None,
    db: Session = Depends(get_db)
):
    service = TrackingService(db)
    assessor = payload.verified_by if payload else "Lead Assessor"
    result = service.reassess_skill(completion_id, verified_by=assessor)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Reassessment failed"))
    return result
