from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[schemas.SkillOut])
def get_skills(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Skill)
    if category:
        query = query.filter(models.Skill.category == category)
    if search:
        query = query.filter(models.Skill.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/categories")
def get_skill_categories(db: Session = Depends(get_db)):
    cats = db.query(models.Skill.category).distinct().all()
    return [c[0] for c in cats]

@router.get("/roles", response_model=List[schemas.RoleOut])
def get_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()
