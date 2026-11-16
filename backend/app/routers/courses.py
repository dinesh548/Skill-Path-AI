from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models, schemas

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("", response_model=List[schemas.CourseOut])
def get_courses(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    skill_id: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Course)
    if provider:
        query = query.filter(models.Course.provider == provider)
    if status:
        query = query.filter(models.Course.status == status)
    if search:
        query = query.filter(models.Course.title.ilike(f"%{search}%"))
    if skill_id:
        query = query.join(models.CourseSkill).filter(models.CourseSkill.skill_id == skill_id)

    courses = query.offset(skip).limit(limit).all()
    results = []
    for c in courses:
        skills_taught = [
            {
                "skill_id": cs.skill_id,
                "skill_name": cs.skill.name if cs.skill else "Unknown",
                "proficiency_gain": cs.proficiency_gain,
                "target_level_taught": cs.target_level_taught
            }
            for cs in c.skills_taught
        ]
        prereqs = [
            {
                "prerequisite_course_id": p.prerequisite_course_id,
                "title": p.prerequisite_course.title if p.prerequisite_course else "Unknown",
                "is_mandatory": p.is_mandatory
            }
            for p in c.prerequisites
        ]
        results.append({
            "id": c.id,
            "title": c.title,
            "provider": c.provider,
            "cost": float(c.cost),
            "duration_hours": c.duration_hours,
            "capacity": c.capacity,
            "enrolled_count": c.enrolled_count,
            "start_date": c.start_date,
            "end_date": c.end_date,
            "status": c.status,
            "description": c.description,
            "skills_taught": skills_taught,
            "prerequisites": prereqs
        })
    return results

@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: str, db: Session = Depends(get_db)):
    c = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")

    skills_taught = [
        {
            "skill_id": cs.skill_id,
            "skill_name": cs.skill.name if cs.skill else "Unknown",
            "proficiency_gain": cs.proficiency_gain,
            "target_level_taught": cs.target_level_taught
        }
        for cs in c.skills_taught
    ]
    prereqs = [
        {
            "prerequisite_course_id": p.prerequisite_course_id,
            "title": p.prerequisite_course.title if p.prerequisite_course else "Unknown",
            "is_mandatory": p.is_mandatory
        }
        for p in c.prerequisites
    ]
    return {
        "id": c.id,
        "title": c.title,
        "provider": c.provider,
        "cost": float(c.cost),
        "duration_hours": c.duration_hours,
        "capacity": c.capacity,
        "enrolled_count": c.enrolled_count,
        "start_date": c.start_date,
        "end_date": c.end_date,
        "status": c.status,
        "description": c.description,
        "skills_taught": skills_taught,
        "prerequisites": prereqs
    }
