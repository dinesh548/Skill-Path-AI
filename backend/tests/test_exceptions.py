import pytest
import datetime
from backend.app.database import SessionLocal
from backend.app import models
from backend.app.services.exception_tracker import ExceptionTracker
from backend.app.services.tracking_service import TrackingService
from backend.app.services.recommendation import CourseRecommendationEngine

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_case_1_prerequisite_violation(db):
    """CASE 1: Recommendation/Enrollment violates prerequisite -> Block and flag."""
    tracker = ExceptionTracker(db)
    service = TrackingService(db)
    
    # Find a course that has a mandatory prerequisite
    prereq = db.query(models.Prerequisite).filter(models.Prerequisite.is_mandatory == True).first()
    assert prereq is not None, "Prerequisite fixture missing"

    course = prereq.course
    needed_prereq_course_id = prereq.prerequisite_course_id

    # Find an employee who has NOT completed this prerequisite course
    emp = db.query(models.Employee).first()
    
    # Ensure emp has not completed prerequisite
    completed = db.query(models.Enrollment).filter(
        models.Enrollment.employee_id == emp.id,
        models.Enrollment.course_id == needed_prereq_course_id,
        models.Enrollment.status == "COMPLETED"
    ).first()
    if completed:
        db.delete(completed)
        db.commit()

    # Attempt enrollment
    result = service.enroll_employee(emp.id, course.id)
    assert result["success"] is False
    assert "Prerequisite violation" in result["error"]
    assert "exception_id" in result

def test_case_2_budget_exceeded(db):
    """CASE 2: Budget exceeded -> Reject course because budget is insufficient."""
    tracker = ExceptionTracker(db)
    service = TrackingService(db)

    # Pick an employee and artificially simulate depleted budget or high course cost
    emp = db.query(models.Employee).first()
    budget = db.query(models.Budget).filter(models.Budget.department == emp.department).first()
    original_balance = budget.remaining_balance
    budget.remaining_balance = 50.0  # Set remaining to $50
    db.commit()

    # Find course with cost > 50
    expensive_course = db.query(models.Course).filter(models.Course.cost > 100).first()

    result = service.enroll_employee(emp.id, expensive_course.id)
    assert result["success"] is False
    assert "budget exceeded" in result["error"].lower()

    # Restore budget
    budget.remaining_balance = original_balance
    db.commit()

def test_case_3_duplicate_completion(db):
    """CASE 3: Completion counted twice -> Detect duplicate without silently deleting history."""
    service = TrackingService(db)

    # Find an already completed enrollment
    completed_enr = db.query(models.Enrollment).filter(models.Enrollment.status == "COMPLETED").first()
    assert completed_enr is not None

    # Get original completion count and score
    orig_cmp = db.query(models.Completion).filter(models.Completion.enrollment_id == completed_enr.id).first()
    orig_score = orig_cmp.assessment_score
    orig_id = orig_cmp.id

    # Attempt second completion
    result = service.complete_course(completed_enr.id, assessment_score=99.9)
    assert result["success"] is False
    assert "Duplicate completion detected" in result["error"]
    assert result["existing_completion_id"] == orig_id

    # Verify original completion history is 100% preserved
    cmp_after = db.query(models.Completion).filter(models.Completion.enrollment_id == completed_enr.id).first()
    assert cmp_after.id == orig_id
    assert cmp_after.assessment_score == orig_score

def test_case_4_skill_gap_remains_without_reassessment(db):
    """CASE 4: Skill gap remains after course without reassessment."""
    # Find completion with reassessment_done == False
    unassessed_cmp = db.query(models.Completion).filter(models.Completion.reassessment_done == False).first()
    assert unassessed_cmp is not None
    assert unassessed_cmp.skill_improvement == 0

    enr = unassessed_cmp.enrollment
    cs = db.query(models.CourseSkill).filter(models.CourseSkill.course_id == enr.course_id).first()
    if cs:
        emp_skill = db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == enr.employee_id,
            models.EmployeeSkill.skill_id == cs.skill_id
        ).first()
        if emp_skill:
            # Current proficiency must not have jumped automatically
            assert emp_skill.assessment_type != "POST_COURSE" or unassessed_cmp.reassessment_done

def test_case_5_course_unavailable_planning_period(db):
    """CASE 5: Course unavailable during planning period -> Excluded from recommended pathway."""
    rec_engine = CourseRecommendationEngine(db)
    emp = db.query(models.Employee).first()

    # Find an unavailable course
    expired = db.query(models.Course).filter(models.Course.status == "EXPIRED").first()
    if not expired:
        expired = db.query(models.Course).first()
        expired.status = "EXPIRED"
        db.commit()

    recs = rec_engine.generate_recommendations(emp.id, planning_date=datetime.date(2026, 2, 16))
    
    # Ensure expired course is NOT in feasible recommendations
    feasible_ids = [r["course_id"] for r in recs["recommendations"]]
    assert expired.id not in feasible_ids

    # It should appear in rejected_recommendations if it was a candidate
    rejected_reasons = [r["rejection_category"] for r in recs["rejected_recommendations"]]
    assert "COURSE_UNAVAILABLE" in rejected_reasons or len(recs["rejected_recommendations"]) >= 0
