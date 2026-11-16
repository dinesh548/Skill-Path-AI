from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app import models
from backend.app.services.gap_analysis import SkillGapEngine
from backend.app.services.metrics_service import MetricsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    metrics_svc = MetricsService(db)
    gap_engine = SkillGapEngine(db)

    # Summary counts
    total_employees = db.query(models.Employee).filter(models.Employee.status == "ACTIVE").count()
    total_courses = db.query(models.Course).count()
    total_skills = db.query(models.Skill).count()
    total_open_exceptions = db.query(models.ExceptionRecord).filter(
        models.ExceptionRecord.resolution_status == "OPEN"
    ).count()

    # Evaluation metrics
    evaluation_data = metrics_svc.calculate_evaluation_metrics()

    # Department gaps
    dept_gaps = gap_engine.get_department_skill_gaps()

    # Top skill shortages
    top_shortages = gap_engine.get_top_skill_shortages(limit=10)

    # Skill proficiency distribution (0 to 5)
    prof_dist = (
        db.query(models.EmployeeSkill.current_proficiency, func.count(models.EmployeeSkill.id))
        .group_by(models.EmployeeSkill.current_proficiency)
        .all()
    )
    prof_map = {p[0]: p[1] for p in prof_dist}
    proficiency_distribution = [
        {"proficiency_level": lvl, "label": f"Level {lvl}", "count": prof_map.get(lvl, 0)}
        for lvl in range(6)
    ]

    # Enrollment status distribution
    status_dist = (
        db.query(models.Enrollment.status, func.count(models.Enrollment.id))
        .group_by(models.Enrollment.status)
        .all()
    )
    enrollment_status_distribution = [
        {"status": s[0], "count": s[1]} for s in status_dist
    ]

    # Department budget breakdown
    budgets = db.query(models.Budget).all()
    budget_breakdown = [
        {
            "department": b.department,
            "allocated": float(b.allocated_amount),
            "spent": float(b.spent_amount),
            "remaining": float(b.remaining_balance),
            "utilization_pct": round(float(b.spent_amount) / float(b.allocated_amount) * 100, 1) if float(b.allocated_amount) > 0 else 0.0
        }
        for b in budgets
    ]

    return {
        "kpis": {
            "total_employees": total_employees,
            "total_courses": total_courses,
            "total_skills": total_skills,
            "total_skill_gaps": next(m["value"] for m in evaluation_data["metrics"] if m["metric_id"] == "MTR-01"),
            "learning_completion_rate": next(m["value"] for m in evaluation_data["metrics"] if m["metric_id"] == "MTR-04"),
            "budget_utilization_pct": next(m["value"] for m in evaluation_data["metrics"] if m["metric_id"] == "MTR-05"),
            "avg_skill_improvement": next(m["value"] for m in evaluation_data["metrics"] if m["metric_id"] == "MTR-03"),
            "open_exceptions_count": total_open_exceptions
        },
        "evaluation_metrics": evaluation_data["metrics"],
        "department_skill_gaps": dept_gaps,
        "top_skill_shortages": top_shortages,
        "proficiency_distribution": proficiency_distribution,
        "enrollment_status_distribution": enrollment_status_distribution,
        "budget_breakdown": budget_breakdown
    }
