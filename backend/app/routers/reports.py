import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app import models
from backend.app.services.gap_analysis import SkillGapEngine
from backend.app.services.recommendation import CourseRecommendationEngine

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/export/skill-gaps")
def export_skill_gaps(db: Session = Depends(get_db)):
    """Export all employee skill gaps as CSV."""
    engine = SkillGapEngine(db)
    employees = db.query(models.Employee).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Employee ID", "Employee Name", "Department", "Role",
        "Skill ID", "Skill Name", "Category", "Current Proficiency",
        "Target Proficiency", "Gap", "Severity", "Importance Weight", "Mandatory"
    ])

    for emp in employees:
        res = engine.calculate_employee_gaps(emp.id)
        if res:
            for s in res["skills"]:
                if s["gap"] > 0:
                    writer.writerow([
                        emp.id, emp.name, emp.department, emp.role.title,
                        s["skill_id"], s["skill_name"], s["category"],
                        s["current_proficiency"], s["required_proficiency"],
                        s["gap"], s["severity"], s["importance_weight"], s["is_mandatory"]
                    ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skill_gaps_report.csv"}
    )

@router.get("/export/recommendations")
def export_recommendations(db: Session = Depends(get_db)):
    """Export active course recommendations as CSV."""
    engine = CourseRecommendationEngine(db)
    employees = db.query(models.Employee).limit(50).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Employee ID", "Employee Name", "Department", "Course ID",
        "Course Title", "Primary Skill", "Skill Gap", "Severity",
        "Priority Score", "Duration Hours", "Cost", "Available Seats", "Explanation"
    ])

    for emp in employees:
        res = engine.generate_recommendations(emp.id)
        for rec in res.get("recommendations", []):
            writer.writerow([
                emp.id, emp.name, emp.department, rec["course_id"],
                rec["course_title"], rec["primary_skill"], rec["skill_gap"],
                rec["gap_severity"], rec["priority_score"], rec["duration_hours"],
                rec["cost"], rec["available_seats"], rec["explanation"]
            ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=course_recommendations_report.csv"}
    )

@router.get("/export/exceptions")
def export_exceptions(db: Session = Depends(get_db)):
    """Export exception audit log as CSV."""
    exceptions = db.query(models.ExceptionRecord).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Issue ID", "Employee ID", "Course ID", "Issue Type",
        "Severity", "Expected Result", "Actual Result",
        "Detection Date", "Resolution Status", "Notes"
    ])

    for e in exceptions:
        writer.writerow([
            e.issue_id, e.employee_id or "N/A", e.course_id or "N/A",
            e.issue_type, e.severity, e.expected_result, e.actual_result,
            e.detection_date.isoformat(), e.resolution_status, e.notes or ""
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=exception_audit_report.csv"}
    )

@router.get("/export/learning-outcomes")
def export_learning_outcomes(db: Session = Depends(get_db)):
    """Export verified course completions and reassessment outcomes as CSV."""
    completions = db.query(models.Completion).join(models.Enrollment).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Completion ID", "Enrollment ID", "Employee ID", "Employee Name",
        "Department", "Course ID", "Course Title", "Completion Date",
        "Assessment Score", "Reassessment Done", "Previous Proficiency",
        "New Proficiency", "Skill Improvement"
    ])

    for c in completions:
        enr = c.enrollment
        writer.writerow([
            c.id, c.enrollment_id, enr.employee_id, enr.employee.name,
            enr.employee.department, enr.course_id, enr.course.title,
            c.completion_date.isoformat(), float(c.assessment_score),
            c.reassessment_done, c.previous_proficiency or 0,
            c.new_proficiency or 0, c.skill_improvement
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=learning_outcomes_report.csv"}
    )
