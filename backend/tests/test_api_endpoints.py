import pytest
from backend.app.database import SessionLocal
from backend.app import models, schemas
from backend.app.routers import (
    employees,
    skills,
    courses,
    recommendations,
    enrollments,
    completions,
    budgets,
    exceptions,
    career,
    analytics,
    reports
)

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_get_employees(db):
    res = employees.get_employees(skip=0, limit=10, db=db)
    assert len(res) > 0
    assert "id" in res[0]
    assert "name" in res[0]
    assert "role_title" in res[0]

def test_get_employee_detail(db):
    res = employees.get_employee("EMP-000001", db=db)
    assert res["id"] == "EMP-000001"
    assert "name" in res
    assert "department" in res

def test_get_employee_skill_gaps(db):
    res = employees.get_employee_skill_gaps("EMP-000001", db=db)
    assert "skills" in res
    assert "overall_readiness_pct" in res
    for s in res["skills"]:
        expected = max(0, s["required_proficiency"] - s["current_proficiency"])
        assert s["gap"] == expected

def test_get_skills(db):
    res = skills.get_skills(skip=0, limit=10, db=db)
    assert len(res) > 0
    assert res[0].name is not None

def test_get_courses(db):
    res = courses.get_courses(skip=0, limit=10, db=db)
    assert len(res) > 0
    assert res[0]["cost"] >= 0

def test_get_recommendations(db):
    res = recommendations.get_recommendations_for_employee("EMP-000001", db=db)
    assert "recommendations" in res
    assert "rejected_recommendations" in res
    assert "learning_pathway" in res

def test_get_budgets(db):
    res = budgets.get_budgets(db=db)
    assert len(res) > 0
    for b in res:
        assert b["allocated_amount"] >= b["spent_amount"]
        assert round(b["allocated_amount"] - (b["spent_amount"] + b["remaining_balance"]), 2) == 0.0

def test_get_exceptions(db):
    res = exceptions.get_exceptions(db=db)
    assert len(res) >= 5
    types = {e["issue_type"] for e in res}
    assert "PREREQUISITE_VIOLATION" in types
    assert "BUDGET_EXCEEDED" in types
    assert "DUPLICATE_COMPLETION" in types
    assert "UNASSESSED_GAP" in types
    assert "COURSE_UNAVAILABLE" in types

def test_get_career_pathway(db):
    res = career.get_employee_career_pathway("EMP-000001", db=db)
    assert "current_role" in res
    assert "target_role" in res
    assert "career_readiness_pct" in res
    assert len(res["competency_breakdown"]) > 0

def test_get_analytics_dashboard(db):
    res = analytics.get_dashboard_analytics(db=db)
    assert "kpis" in res
    assert "evaluation_metrics" in res
    assert len(res["evaluation_metrics"]) == 10
    assert "department_skill_gaps" in res
    assert "top_skill_shortages" in res
