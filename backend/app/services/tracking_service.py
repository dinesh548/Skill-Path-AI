import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app import models
from backend.app.services.exception_tracker import ExceptionTracker

class TrackingService:
    def __init__(self, db: Session):
        self.db = db
        self.exception_tracker = ExceptionTracker(db)

    def enroll_employee(self, employee_id: str, course_id: str, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Enroll employee in course with validations:
        - Check if already enrolled (prevent duplicates)
        - Check mandatory prerequisites (CASE 1)
        - Check department budget (CASE 2)
        - Check course capacity & availability (CASE 5)
        """
        emp = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not emp:
            return {"success": False, "error": f"Employee {employee_id} not found"}

        course = self.db.query(models.Course).filter(models.Course.id == course_id).first()
        if not course:
            return {"success": False, "error": f"Course {course_id} not found"}

        # Check existing enrollment
        existing_enr = self.db.query(models.Enrollment).filter(
            models.Enrollment.employee_id == employee_id,
            models.Enrollment.course_id == course_id
        ).first()
        if existing_enr:
            return {
                "success": False,
                "error": f"Employee is already enrolled in this course (Status: {existing_enr.status})",
                "enrollment_id": existing_enr.id
            }

        # Check CASE 5: Course availability
        if course.status != "AVAILABLE":
            self.exception_tracker.test_case_5_course_unavailable(course_id)
            return {"success": False, "error": f"Course is currently {course.status} and not accepting enrollments"}

        # Check Course capacity
        if course.enrolled_count >= course.capacity:
            return {"success": False, "error": "Course is at full capacity"}

        # Check CASE 1: Prerequisites
        prereq_check = self.exception_tracker.test_case_1_prerequisite_violation(employee_id, course_id)
        if prereq_check.get("blocked"):
            return {
                "success": False,
                "error": f"Prerequisite violation: Missing courses {prereq_check.get('missing_prerequisites')}",
                "exception_id": prereq_check.get("issue_id")
            }

        # Check CASE 2: Department budget
        budget_check = self.exception_tracker.test_case_2_budget_exceeded(employee_id, course_id)
        if budget_check.get("rejected"):
            return {
                "success": False,
                "error": f"Department budget exceeded. Cost: ${budget_check['cost']:.2f}, Remaining: ${budget_check['remaining_budget']:.2f}",
                "exception_id": budget_check.get("issue_id")
            }

        # Create enrollment
        enr_id = f"ENR-{employee_id}-{course_id}"
        cost = float(course.cost)
        status = "APPROVED" if auto_approve else "PENDING"
        today = datetime.date.today()

        enr = models.Enrollment(
            id=enr_id,
            employee_id=employee_id,
            course_id=course_id,
            enrollment_date=today,
            status=status,
            approved_by="System" if auto_approve else None,
            approval_date=today if auto_approve else None,
            cost_charged=cost if auto_approve else 0.00
        )
        self.db.add(enr)

        if auto_approve:
            course.enrolled_count += 1
            # Deduct from budget
            budget = self.db.query(models.Budget).filter(models.Budget.department == emp.department).first()
            if budget:
                budget.spent_amount = float(budget.spent_amount) + cost
                budget.remaining_balance = float(budget.allocated_amount) - float(budget.spent_amount)

        self.db.commit()
        self.db.refresh(enr)
        return {"success": True, "enrollment_id": enr.id, "status": enr.status, "message": "Enrollment created successfully"}

    def approve_enrollment(self, enrollment_id: str, approver: str = "Dept Manager") -> Dict[str, Any]:
        """Approve a pending enrollment, update course seats and department budget."""
        enr = self.db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
        if not enr:
            return {"success": False, "error": "Enrollment not found"}
        if enr.status != "PENDING":
            return {"success": False, "error": f"Enrollment cannot be approved from status: {enr.status}"}

        emp = enr.employee
        course = enr.course
        cost = float(course.cost)

        # Re-check budget
        budget = self.db.query(models.Budget).filter(models.Budget.department == emp.department).first()
        if budget and float(budget.remaining_balance) < cost:
            self.exception_tracker.test_case_2_budget_exceeded(emp.id, course.id)
            return {"success": False, "error": "Insufficient departmental budget to approve enrollment"}

        enr.status = "APPROVED"
        enr.approved_by = approver
        enr.approval_date = datetime.date.today()
        enr.cost_charged = cost
        course.enrolled_count += 1

        if budget:
            budget.spent_amount = float(budget.spent_amount) + cost
            budget.remaining_balance = float(budget.allocated_amount) - float(budget.spent_amount)

        self.db.commit()
        return {"success": True, "enrollment_id": enr.id, "status": enr.status, "message": "Enrollment approved and budget allocated"}

    def start_course(self, enrollment_id: str) -> Dict[str, Any]:
        """Transition enrollment from APPROVED to IN_PROGRESS."""
        enr = self.db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
        if not enr:
            return {"success": False, "error": "Enrollment not found"}
        if enr.status != "APPROVED":
            return {"success": False, "error": f"Only APPROVED enrollments can start (current: {enr.status})"}

        enr.status = "IN_PROGRESS"
        self.db.commit()
        return {"success": True, "enrollment_id": enr.id, "status": enr.status, "message": "Course training commenced"}

    def complete_course(self, enrollment_id: str, assessment_score: float, completion_date: Optional[datetime.date] = None) -> Dict[str, Any]:
        """
        Record course completion.
        CASE 3 check: Detect duplicate completions.
        Important: Attendance != Completion. Completion != Skill improvement.
        Initial proficiency remains unchanged until post-course reassessment is performed!
        """
        enr = self.db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
        if not enr:
            return {"success": False, "error": "Enrollment not found"}

        # Check CASE 3: Duplicate completion detection
        dup_check = self.exception_tracker.test_case_3_duplicate_completion(enrollment_id, assessment_score)
        if dup_check.get("duplicate_detected"):
            return {
                "success": False,
                "error": "Duplicate completion detected for this enrollment",
                "exception_id": dup_check.get("issue_id"),
                "existing_completion_id": dup_check.get("existing_completion_id")
            }

        if enr.status not in ["IN_PROGRESS", "APPROVED"]:
            return {"success": False, "error": f"Cannot complete enrollment in status {enr.status}"}

        c_date = completion_date or datetime.date.today()
        cmp_count = self.db.query(models.Completion).count() + 1
        cmp_id = f"CMP-2026-{cmp_count:06d}"

        completion = models.Completion(
            id=cmp_id,
            enrollment_id=enrollment_id,
            completion_date=c_date,
            assessment_score=assessment_score,
            reassessment_done=False,  # Unassessed initially!
            previous_proficiency=None,
            new_proficiency=None,
            skill_improvement=0,
            certificate_url=f"https://certs.skillpath.ai/2026/{cmp_id}.pdf"
        )
        enr.status = "COMPLETED"
        self.db.add(completion)
        self.db.commit()

        # Log CASE 4 pending reassessment trigger
        self.exception_tracker.test_case_4_unassessed_gap(enrollment_id)

        return {
            "success": True,
            "completion_id": completion.id,
            "enrollment_id": enr.id,
            "status": "COMPLETED",
            "reassessment_done": False,
            "message": "Course completion recorded. Skill reassessment is now pending."
        }

    def reassess_skill(self, completion_id: str, verified_by: str = "Lead Assessor") -> Dict[str, Any]:
        """
        Perform formal post-course skill reassessment.
        Validates the assessment score (must be >= 70.0% to earn proficiency gain).
        Updates EmployeeSkill records and marks reassessment_done=True.
        """
        cmp = self.db.query(models.Completion).filter(models.Completion.id == completion_id).first()
        if not cmp:
            return {"success": False, "error": "Completion record not found"}
        if cmp.reassessment_done:
            return {"success": False, "error": "Reassessment has already been finalized for this completion"}

        enr = cmp.enrollment
        emp_id = enr.employee_id
        course_id = enr.course_id

        # Determine taught skills and potential gain
        course_skills = self.db.query(models.CourseSkill).filter(
            models.CourseSkill.course_id == course_id
        ).all()

        if not course_skills:
            cmp.reassessment_done = True
            self.db.commit()
            return {"success": True, "message": "Reassessment finalized (no specific skills tied to course)"}

        primary_cs = course_skills[0]
        skill_id = primary_cs.skill_id
        gain = primary_cs.proficiency_gain if float(cmp.assessment_score) >= 70.0 else 0

        # Query existing employee skill
        emp_skill = self.db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == emp_id,
            models.EmployeeSkill.skill_id == skill_id
        ).first()

        prev_prof = emp_skill.current_proficiency if emp_skill else 0
        new_prof = min(5, prev_prof + gain)
        improvement = new_prof - prev_prof

        if emp_skill:
            emp_skill.current_proficiency = new_prof
            emp_skill.last_assessed_date = datetime.date.today()
            emp_skill.assessment_type = "POST_COURSE"
            emp_skill.verified_by = verified_by
        else:
            # Create employee skill if didn't exist before
            esk_id = f"ESK-{emp_id}-{skill_id}"
            new_es = models.EmployeeSkill(
                id=esk_id,
                employee_id=emp_id,
                skill_id=skill_id,
                current_proficiency=new_prof,
                last_assessed_date=datetime.date.today(),
                assessment_type="POST_COURSE",
                verified_by=verified_by
            )
            self.db.add(new_es)

        cmp.reassessment_done = True
        cmp.previous_proficiency = prev_prof
        cmp.new_proficiency = new_prof
        cmp.skill_improvement = improvement

        # Check if there is an open UNASSESSED_GAP exception for this and resolve it!
        open_exc = self.db.query(models.ExceptionRecord).filter(
            models.ExceptionRecord.employee_id == emp_id,
            models.ExceptionRecord.course_id == course_id,
            models.ExceptionRecord.issue_type == "UNASSESSED_GAP",
            models.ExceptionRecord.resolution_status == "OPEN"
        ).first()
        if open_exc:
            open_exc.resolution_status = "RESOLVED"
            open_exc.notes = f"Reassessment completed successfully. Score: {cmp.assessment_score}%, Gain: +{improvement} proficiency levels."

        self.db.commit()

        return {
            "success": True,
            "completion_id": cmp.id,
            "skill_id": skill_id,
            "previous_proficiency": prev_prof,
            "new_proficiency": new_prof,
            "skill_improvement": improvement,
            "message": f"Skill reassessment successful! Proficiency upgraded from {prev_prof} to {new_prof} (+{improvement})."
        }

    def cancel_enrollment(self, enrollment_id: str, reason: str = "User request") -> Dict[str, Any]:
        """Cancel an enrollment and release reserved seats & budget if previously approved."""
        enr = self.db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
        if not enr:
            return {"success": False, "error": "Enrollment not found"}
        if enr.status in ["COMPLETED", "CANCELLED"]:
            return {"success": False, "error": f"Cannot cancel enrollment in status {enr.status}"}

        prev_status = enr.status
        cost = float(enr.cost_charged)
        enr.status = "CANCELLED"

        # Refund budget and seat if it was APPROVED or IN_PROGRESS
        if prev_status in ["APPROVED", "IN_PROGRESS"]:
            course = enr.course
            course.enrolled_count = max(0, course.enrolled_count - 1)
            budget = self.db.query(models.Budget).filter(models.Budget.department == enr.employee.department).first()
            if budget and cost > 0:
                budget.spent_amount = max(0.0, float(budget.spent_amount) - cost)
                budget.remaining_balance = float(budget.allocated_amount) - float(budget.spent_amount)

        self.db.commit()
        return {"success": True, "enrollment_id": enr.id, "status": "CANCELLED", "message": f"Enrollment cancelled ({reason})"}
