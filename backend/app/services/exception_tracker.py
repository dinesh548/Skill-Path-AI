import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app import models

class ExceptionTracker:
    def __init__(self, db: Session):
        self.db = db

    def get_all_exceptions(
        self,
        issue_type: Optional[str] = None,
        severity: Optional[str] = None,
        resolution_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve recorded exceptions with optional filters."""
        query = self.db.query(models.ExceptionRecord)
        if issue_type:
            query = query.filter(models.ExceptionRecord.issue_type == issue_type)
        if severity:
            query = query.filter(models.ExceptionRecord.severity == severity)
        if resolution_status:
            query = query.filter(models.ExceptionRecord.resolution_status == resolution_status)

        exceptions = query.order_by(models.ExceptionRecord.detection_date.desc()).all()
        results = []
        for e in exceptions:
            emp_name = e.employee.name if e.employee else "N/A"
            course_title = e.course.title if e.course else "N/A"
            dept = e.employee.department if e.employee else "N/A"
            results.append({
                "issue_id": e.issue_id,
                "employee_id": e.employee_id,
                "employee_name": emp_name,
                "department": dept,
                "course_id": e.course_id,
                "course_title": course_title,
                "issue_type": e.issue_type,
                "severity": e.severity,
                "expected_result": e.expected_result,
                "actual_result": e.actual_result,
                "detection_date": e.detection_date.isoformat(),
                "resolution_status": e.resolution_status,
                "notes": e.notes
            })
        return results

    def record_exception(
        self,
        issue_type: str,
        severity: str,
        expected_result: str,
        actual_result: str,
        employee_id: Optional[str] = None,
        course_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> models.ExceptionRecord:
        """Dynamically record an exception event in the persistent audit trail."""
        count = self.db.query(models.ExceptionRecord).count() + 1
        issue_id = f"ISS-{count:06d}"
        
        # Verify unique issue_id
        while self.db.query(models.ExceptionRecord).filter(models.ExceptionRecord.issue_id == issue_id).first():
            count += 1
            issue_id = f"ISS-{count:06d}"

        exc = models.ExceptionRecord(
            issue_id=issue_id,
            employee_id=employee_id,
            course_id=course_id,
            issue_type=issue_type,
            severity=severity,
            expected_result=expected_result,
            actual_result=actual_result,
            detection_date=datetime.datetime.utcnow(),
            resolution_status="OPEN",
            notes=notes
        )
        self.db.add(exc)
        self.db.commit()
        self.db.refresh(exc)
        return exc

    def update_resolution(self, issue_id: str, new_status: str, notes: Optional[str] = None) -> Optional[models.ExceptionRecord]:
        """Update resolution status (OPEN, RESOLVED, ACKNOWLEDGED, SUPPRESSED)."""
        exc = self.db.query(models.ExceptionRecord).filter(models.ExceptionRecord.issue_id == issue_id).first()
        if not exc:
            return None
        exc.resolution_status = new_status
        if notes:
            exc.notes = f"{exc.notes or ''}\nResolution Note ({datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')}): {notes}".strip()
        self.db.commit()
        self.db.refresh(exc)
        return exc

    def test_case_1_prerequisite_violation(self, employee_id: str, course_id: str) -> Dict[str, Any]:
        """
        CASE 1: Recommendation violates prerequisite.
        Expected result: Block recommendation and flag violation.
        """
        prereqs = self.db.query(models.Prerequisite).filter(
            models.Prerequisite.course_id == course_id,
            models.Prerequisite.is_mandatory == True
        ).all()

        completed_courses = {
            e.course_id for e in self.db.query(models.Enrollment).filter(
                models.Enrollment.employee_id == employee_id,
                models.Enrollment.status == "COMPLETED"
            ).all()
        }

        unsatisfied = [p.prerequisite_course_id for p in prereqs if p.prerequisite_course_id not in completed_courses]

        if unsatisfied:
            exc = self.record_exception(
                issue_type="PREREQUISITE_VIOLATION",
                severity="HIGH",
                expected_result=f"Block enrollment/recommendation for {course_id} due to unsatisfied prerequisites: {unsatisfied}.",
                actual_result=f"Blocked recommendation. Prerequisite(s) {unsatisfied} missing.",
                employee_id=employee_id,
                course_id=course_id,
                notes="Automated rule check detected missing prerequisite completion."
            )
            return {"blocked": True, "issue_id": exc.issue_id, "missing_prerequisites": unsatisfied}
        return {"blocked": False, "message": "All prerequisites satisfied."}

    def test_case_2_budget_exceeded(self, employee_id: str, course_id: str) -> Dict[str, Any]:
        """
        CASE 2: Budget exceeded.
        Expected result: Reject or flag the course because the department budget is insufficient.
        """
        emp = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        course = self.db.query(models.Course).filter(models.Course.id == course_id).first()
        if not emp or not course:
            return {"error": "Invalid employee or course ID"}

        budget = self.db.query(models.Budget).filter(models.Budget.department == emp.department).first()
        remaining = float(budget.remaining_balance) if budget else 0.0
        cost = float(course.cost)

        if cost > remaining:
            exc = self.record_exception(
                issue_type="BUDGET_EXCEEDED",
                severity="CRITICAL",
                expected_result=f"Reject course {course_id} (${cost:.2f}) because {emp.department} remaining budget (${remaining:.2f}) is insufficient.",
                actual_result=f"Department budget exceeded by ${(cost - remaining):.2f}. Enrollment/Recommendation rejected.",
                employee_id=employee_id,
                course_id=course_id,
                notes="Automated budget gate intercepted transaction."
            )
            return {"rejected": True, "issue_id": exc.issue_id, "cost": cost, "remaining_budget": remaining}
        return {"rejected": False, "cost": cost, "remaining_budget": remaining}

    def test_case_3_duplicate_completion(self, enrollment_id: str, score: float = 85.0) -> Dict[str, Any]:
        """
        CASE 3: Completion counted twice.
        Expected result: Detect duplicate completion without silently deleting history.
        """
        existing = self.db.query(models.Completion).filter(models.Completion.enrollment_id == enrollment_id).first()
        if existing:
            enr = self.db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
            exc = self.record_exception(
                issue_type="DUPLICATE_COMPLETION",
                severity="MEDIUM",
                expected_result=f"Detect duplicate completion for {enrollment_id} and maintain original completion history intact.",
                actual_result=f"Duplicate completion blocked. Prior completion on {existing.completion_date} preserved (Score: {existing.assessment_score}%).",
                employee_id=enr.employee_id if enr else None,
                course_id=enr.course_id if enr else None,
                notes=f"Attempted secondary completion for existing certificate ID: {existing.id}."
            )
            return {
                "duplicate_detected": True,
                "issue_id": exc.issue_id,
                "existing_completion_id": existing.id,
                "message": "Duplicate completion safely intercepted without modifying historical record."
            }
        return {"duplicate_detected": False}

    def test_case_4_unassessed_gap(self, enrollment_id: str) -> Dict[str, Any]:
        """
        CASE 4: Skill gap remains after course without reassessment.
        Expected result: Keep existing proficiency unchanged and flag pending reassessment.
        """
        cmp = self.db.query(models.Completion).filter(models.Completion.enrollment_id == enrollment_id).first()
        if cmp and not cmp.reassessment_done:
            enr = cmp.enrollment
            exc = self.record_exception(
                issue_type="UNASSESSED_GAP",
                severity="HIGH",
                expected_result="Keep existing proficiency unchanged and flag pending reassessment.",
                actual_result="Skill proficiency unchanged. Pending formal reassessment.",
                employee_id=enr.employee_id,
                course_id=enr.course_id,
                notes="Course completed, but skill proficiency remains at prior level until assessment exam is submitted."
            )
            return {"unassessed": True, "issue_id": exc.issue_id, "message": "Proficiency unchanged; reassessment required."}
        return {"unassessed": False}

    def test_case_5_course_unavailable(self, course_id: str, planning_date: datetime.date = datetime.date(2026, 2, 16)) -> Dict[str, Any]:
        """
        CASE 5: Course unavailable during planning period.
        Expected result: Exclude the course from the recommended learning pathway.
        """
        course = self.db.query(models.Course).filter(models.Course.id == course_id).first()
        if not course:
            return {"error": "Course not found"}

        unavailable = (course.status != "AVAILABLE" or course.end_date < planning_date)
        if unavailable:
            exc = self.record_exception(
                issue_type="COURSE_UNAVAILABLE",
                severity="LOW",
                expected_result=f"Exclude course {course_id} from recommended learning pathway due to unavailability.",
                actual_result=f"Course status is {course.status} (End date: {course.end_date}). Excluded from pathway.",
                course_id=course_id,
                notes="Course outside active scheduling window."
            )
            return {"unavailable": True, "issue_id": exc.issue_id, "status": course.status}
        return {"unavailable": False, "status": course.status}
