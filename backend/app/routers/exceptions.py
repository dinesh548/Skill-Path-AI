from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import schemas
from backend.app.services.exception_tracker import ExceptionTracker

router = APIRouter(prefix="/exceptions", tags=["Exceptions"])

@router.get("", response_model=List[schemas.ExceptionOut])
def get_exceptions(
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    resolution_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    tracker = ExceptionTracker(db)
    return tracker.get_all_exceptions(
        issue_type=issue_type,
        severity=severity,
        resolution_status=resolution_status
    )

@router.patch("/{issue_id}/resolve")
def resolve_exception(
    issue_id: str,
    payload: schemas.ExceptionResolveRequest,
    db: Session = Depends(get_db)
):
    tracker = ExceptionTracker(db)
    res = tracker.update_resolution(issue_id, payload.resolution_status, payload.notes)
    if not res:
        raise HTTPException(status_code=404, detail=f"Exception issue {issue_id} not found")
    return {"success": True, "issue_id": issue_id, "resolution_status": res.resolution_status}
