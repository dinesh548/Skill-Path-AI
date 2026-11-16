from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.services.gap_analysis import SkillGapEngine

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=List[schemas.EmployeeOut])
def get_employees(
    department: Optional[str] = None,
    role_id: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Employee)
    if department:
        query = query.filter(models.Employee.department == department)
    if role_id:
        query = query.filter(models.Employee.role_id == role_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Employee.name.ilike(search_pattern)) |
            (models.Employee.id.ilike(search_pattern)) |
            (models.Employee.email.ilike(search_pattern))
        )
    employees = query.offset(skip).limit(limit).all()
    results = []
    for emp in employees:
        results.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "department": emp.department,
            "role_id": emp.role_id,
            "role_title": emp.role.title if emp.role else None,
            "role_level": emp.role.level if emp.role else None,
            "hire_date": emp.hire_date,
            "status": emp.status,
            "created_at": emp.created_at,
            "updated_at": emp.updated_at
        })
    return results

@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "department": emp.department,
        "role_id": emp.role_id,
        "role_title": emp.role.title if emp.role else None,
        "role_level": emp.role.level if emp.role else None,
        "hire_date": emp.hire_date,
        "status": emp.status,
        "created_at": emp.created_at,
        "updated_at": emp.updated_at
    }

@router.post("", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check if role exists
    role = db.query(models.Role).filter(models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role {payload.role_id} does not exist")
    
    # Check email uniqueness
    existing = db.query(models.Employee).filter(models.Employee.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    # Generate sequential EMP-XXXXXX id
    count = db.query(models.Employee).count() + 1
    new_id = f"EMP-{count:06d}"
    while db.query(models.Employee).filter(models.Employee.id == new_id).first():
        count += 1
        new_id = f"EMP-{count:06d}"

    emp = models.Employee(
        id=new_id,
        name=payload.name,
        email=payload.email,
        department=payload.department,
        role_id=payload.role_id,
        hire_date=date.today(),
        status="ACTIVE"
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    return {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "department": emp.department,
        "role_id": emp.role_id,
        "role_title": role.title,
        "role_level": role.level,
        "hire_date": emp.hire_date,
        "status": emp.status,
        "created_at": emp.created_at,
        "updated_at": emp.updated_at
    }

@router.get("/{employee_id}/skills", response_model=List[schemas.EmployeeSkillOut])
def get_employee_skills(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    skills = db.query(models.EmployeeSkill).filter(models.EmployeeSkill.employee_id == employee_id).all()
    results = []
    for es in skills:
        results.append({
            "skill_id": es.skill_id,
            "skill_name": es.skill.name if es.skill else "Unknown",
            "category": es.skill.category if es.skill else "General",
            "current_proficiency": es.current_proficiency,
            "last_assessed_date": es.last_assessed_date,
            "assessment_type": es.assessment_type,
            "verified_by": es.verified_by
        })
    return results

@router.get("/{employee_id}/skill-gaps")
def get_employee_skill_gaps(employee_id: str, db: Session = Depends(get_db)):
    engine = SkillGapEngine(db)
    result = engine.calculate_employee_gaps(employee_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return result
