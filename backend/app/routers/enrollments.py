from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.services.tracking_service import TrackingService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.get("", response_model=List[schemas.EnrollmentOut])
def get_enrollments(
    employee_id: Optional[str] = None,
    course_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Enrollment)
    if employee_id:
        query = query.filter(models.Enrollment.employee_id == employee_id)
    if course_id:
        query = query.filter(models.Enrollment.course_id == course_id)
    if status:
        query = query.filter(models.Enrollment.status == status)

    enrollments = query.order_by(models.Enrollment.enrollment_date.desc()).offset(skip).limit(limit).all()
    results = []
    for enr in enrollments:
        cmp = enr.completion
        results.append({
            "id": enr.id,
            "employee_id": enr.employee_id,
            "employee_name": enr.employee.name if enr.employee else None,
            "department": enr.employee.department if enr.employee else None,
            "course_id": enr.course_id,
            "course_title": enr.course.title if enr.course else None,
            "enrollment_date": enr.enrollment_date,
            "status": enr.status,
            "approved_by": enr.approved_by,
            "approval_date": enr.approval_date,
            "cost_charged": float(enr.cost_charged),
            "completion_id": cmp.id if cmp else None,
            "assessment_score": float(cmp.assessment_score) if cmp else None,
            "reassessment_done": cmp.reassessment_done if cmp else None
        })
    return results

@router.post("", status_code=201)
def create_enrollment(
    payload: schemas.EnrollmentCreate,
    db: Session = Depends(get_db)
):
    service = TrackingService(db)
    result = service.enroll_employee(
        employee_id=payload.employee_id,
        course_id=payload.course_id,
        auto_approve=payload.auto_approve
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Enrollment failed"))
    return result

@router.patch("/{enrollment_id}")
def update_enrollment(
    enrollment_id: str,
    payload: schemas.EnrollmentUpdate,
    db: Session = Depends(get_db)
):
    service = TrackingService(db)
    if payload.status == "APPROVED":
        approver = payload.approved_by or "Dept Manager"
        res = service.approve_enrollment(enrollment_id, approver)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error"))
        return res
    elif payload.status == "IN_PROGRESS":
        res = service.start_course(enrollment_id)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error"))
        return res
    elif payload.status == "CANCELLED":
        res = service.cancel_enrollment(enrollment_id, reason="Manager / User action")
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error"))
        return res
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported status transition to {payload.status}")
