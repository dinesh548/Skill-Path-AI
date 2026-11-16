from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("", response_model=List[schemas.BudgetOut])
def get_budgets(db: Session = Depends(get_db)):
    budgets = db.query(models.Budget).all()
    results = []
    for b in budgets:
        alloc = float(b.allocated_amount)
        spent = float(b.spent_amount)
        rem = float(b.remaining_balance)
        util_pct = round((spent / alloc * 100) if alloc > 0 else 0.0, 1)
        results.append({
            "id": b.id,
            "department": b.department,
            "fiscal_year": b.fiscal_year,
            "allocated_amount": alloc,
            "spent_amount": spent,
            "remaining_balance": rem,
            "utilization_pct": util_pct,
            "last_updated": b.last_updated
        })
    return results

@router.get("/{department}", response_model=schemas.BudgetOut)
def get_department_budget(department: str, db: Session = Depends(get_db)):
    # Support case-insensitive or exact match
    b = db.query(models.Budget).filter(models.Budget.department.ilike(department)).first()
    if not b:
        raise HTTPException(status_code=404, detail=f"Budget for department '{department}' not found")
    alloc = float(b.allocated_amount)
    spent = float(b.spent_amount)
    rem = float(b.remaining_balance)
    util_pct = round((spent / alloc * 100) if alloc > 0 else 0.0, 1)
    return {
        "id": b.id,
        "department": b.department,
        "fiscal_year": b.fiscal_year,
        "allocated_amount": alloc,
        "spent_amount": spent,
        "remaining_balance": rem,
        "utilization_pct": util_pct,
        "last_updated": b.last_updated
    }
