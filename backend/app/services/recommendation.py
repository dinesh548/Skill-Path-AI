import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app import models
from backend.app.services.gap_analysis import SkillGapEngine

class CourseRecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.gap_engine = SkillGapEngine(db)

    def generate_recommendations(self, employee_id: str, planning_date: Optional[datetime.date] = None) -> Dict[str, Any]:
        """
        Executes the 12-step intelligent recommendation algorithm:
        1. Current role
        2. Role skill requirements
        3. Current employee proficiency
        4. Calculate missing skills
        5. Identify courses teaching missing skills
        6. Verify prerequisites
        7. Verify course availability
        8. Check available seats
        9. Check departmental budget
        10. Calculate course priority score
        11. Recommend feasible courses with explanations
        12. Build an ordered learning pathway sequence
        """
        if planning_date is None:
            planning_date = datetime.date(2026, 2, 16)

        # Step 1, 2, 3, 4: Skill Gaps Analysis
        emp = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not emp:
            return {"error": f"Employee {employee_id} not found"}

        gap_data = self.gap_engine.calculate_employee_gaps(employee_id)
        if not gap_data:
            return {"error": "Unable to calculate employee skill gaps"}

        # Identify missing skills with gap > 0
        missing_skills = [s for s in gap_data["skills"] if s["gap"] > 0]
        missing_skill_ids = {s["skill_id"] for s in missing_skills}
        gap_lookup = {s["skill_id"]: s for s in missing_skills}

        if not missing_skills:
            return {
                "employee_id": emp.id,
                "employee_name": emp.name,
                "department": emp.department,
                "role_title": emp.role.title,
                "missing_skills_count": 0,
                "recommendations": [],
                "rejected_recommendations": [],
                "learning_pathway": [],
                "message": "Employee currently meets all proficiency targets for their role."
            }

        # Step 5: Identify courses that teach these missing skills
        # Query CourseSkills matching missing_skill_ids
        course_skills = self.db.query(models.CourseSkill).filter(
            models.CourseSkill.skill_id.in_(missing_skill_ids)
        ).all()
        candidate_course_ids = {cs.course_id for cs in course_skills}

        # Retrieve candidate courses
        candidate_courses = self.db.query(models.Course).filter(
            models.Course.id.in_(candidate_course_ids)
        ).all()

        # Retrieve completed courses by employee (for prerequisite verification)
        completed_enrollments = self.db.query(models.Enrollment).filter(
            models.Enrollment.employee_id == employee_id,
            models.Enrollment.status == "COMPLETED"
        ).all()
        completed_course_ids = {enr.course_id for enr in completed_enrollments}

        # Also retrieve active/pending enrollments to avoid duplicate recommendations
        active_enrollments = self.db.query(models.Enrollment).filter(
            models.Enrollment.employee_id == employee_id,
            models.Enrollment.status.in_(["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED"])
        ).all()
        already_enrolled_course_ids = {enr.course_id for enr in active_enrollments}

        # Department budget
        dept_budget = self.db.query(models.Budget).filter(
            models.Budget.department == emp.department
        ).first()
        remaining_budget = float(dept_budget.remaining_balance) if dept_budget else 0.0

        feasible_recommendations = []
        rejected_recommendations = []

        # Evaluate each candidate course through steps 6-10
        for course in candidate_courses:
            # Skip if already enrolled or completed
            if course.id in already_enrolled_course_ids:
                continue

            # Skills taught by this course that address employee gaps
            skills_taught = [
                cs for cs in course.skills_taught if cs.skill_id in missing_skill_ids
            ]
            if not skills_taught:
                continue

            primary_cs = skills_taught[0]
            skill_info = gap_lookup[primary_cs.skill_id]
            skill_name = skill_info["skill_name"]
            gap_value = skill_info["gap"]
            severity = skill_info["severity"]

            # Step 6: Verify Prerequisites
            prereqs = self.db.query(models.Prerequisite).filter(
                models.Prerequisite.course_id == course.id
            ).all()
            missing_prereqs = []
            for p in prereqs:
                if p.is_mandatory and p.prerequisite_course_id not in completed_course_ids:
                    missing_prereqs.append(p.prerequisite_course.title)

            if missing_prereqs:
                rejection_reason = (
                    f"Rejected {course.title} because prerequisite(s) "
                    f"[{', '.join(missing_prereqs)}] have not been completed."
                )
                rejected_recommendations.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "skill_targeted": skill_name,
                    "rejection_category": "PREREQUISITE_VIOLATION",
                    "reason": rejection_reason,
                    "cost": float(course.cost),
                    "duration_hours": course.duration_hours
                })
                continue

            # Step 7: Verify Course Availability & Dates
            is_active = (course.status == "AVAILABLE")
            is_in_window = (course.end_date >= planning_date)
            if not is_active or not is_in_window:
                rejection_reason = (
                    f"Rejected {course.title} because the course is unavailable "
                    f"(Status: {course.status}, Schedule: {course.start_date} to {course.end_date}) "
                    f"during the active planning period."
                )
                rejected_recommendations.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "skill_targeted": skill_name,
                    "rejection_category": "COURSE_UNAVAILABLE",
                    "reason": rejection_reason,
                    "cost": float(course.cost),
                    "duration_hours": course.duration_hours
                })
                continue

            # Step 8: Check Available Seats
            available_seats = course.capacity - course.enrolled_count
            if available_seats <= 0:
                rejection_reason = (
                    f"Rejected {course.title} because the course is at full capacity "
                    f"({course.enrolled_count}/{course.capacity} seats filled)."
                )
                rejected_recommendations.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "skill_targeted": skill_name,
                    "rejection_category": "CAPACITY_FULL",
                    "reason": rejection_reason,
                    "cost": float(course.cost),
                    "duration_hours": course.duration_hours
                })
                continue

            # Step 9: Check Departmental Budget
            course_cost = float(course.cost)
            if course_cost > remaining_budget:
                rejection_reason = (
                    f"Rejected {course.title} (${course_cost:,.2f}) because "
                    f"{emp.department} department remaining budget (${remaining_budget:,.2f}) is insufficient."
                )
                rejected_recommendations.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "skill_targeted": skill_name,
                    "rejection_category": "BUDGET_EXCEEDED",
                    "reason": rejection_reason,
                    "cost": course_cost,
                    "duration_hours": course.duration_hours
                })
                continue

            # Step 10: Calculate Priority Score
            # Priority formula incorporating:
            # - Gap severity weight (Critical: 40, High: 30, Medium: 20, Low: 10)
            # - Skill importance weight (0.5 - 2.0 multiplier)
            # - Number of missing skills covered
            # - Course cost & duration efficiency
            severity_weights = {"Critical": 40.0, "High": 30.0, "Medium": 20.0, "Low": 10.0, "Met": 0.0}
            base_score = severity_weights.get(severity, 10.0) * skill_info["importance_weight"]
            coverage_bonus = (len(skills_taught) - 1) * 15.0
            efficiency_score = max(5.0, 30.0 - (course.duration_hours / 4.0) - (course_cost / 150.0))
            priority_score = round(base_score + coverage_bonus + efficiency_score, 2)

            # Step 11: Build Positive Explanation
            explanation = (
                f"Recommended {course.title} because the employee has a {skill_name} "
                f"proficiency gap of {gap_value} (Target: {skill_info['required_proficiency']}, "
                f"Current: {skill_info['current_proficiency']}) and meets all prerequisites. "
                f"The course is available ({available_seats} seats remaining) and fits within the "
                f"{emp.department} departmental budget (${course_cost:,.2f} <= ${remaining_budget:,.2f})."
            )

            feasible_recommendations.append({
                "course_id": course.id,
                "course_title": course.title,
                "provider": course.provider,
                "cost": course_cost,
                "duration_hours": course.duration_hours,
                "available_seats": available_seats,
                "skills_covered": [s.skill.name for s in skills_taught],
                "primary_skill": skill_name,
                "skill_gap": gap_value,
                "gap_severity": severity,
                "priority_score": priority_score,
                "explanation": explanation,
                "start_date": str(course.start_date),
                "end_date": str(course.end_date)
            })

        # Sort feasible recommendations by priority score descending
        feasible_recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

        # Step 12: Build an Ordered Learning Pathway
        # Sequence: prioritize foundational / highest gap first, maintain prerequisite ordering
        learning_pathway = []
        cumulative_cost = 0.0
        cumulative_hours = 0

        for idx, rec in enumerate(feasible_recommendations, 1):
            cumulative_cost += rec["cost"]
            cumulative_hours += rec["duration_hours"]
            learning_pathway.append({
                "sequence_step": idx,
                "course_id": rec["course_id"],
                "course_title": rec["course_title"],
                "skill_addressed": rec["primary_skill"],
                "estimated_hours": rec["duration_hours"],
                "cost": rec["cost"],
                "cumulative_hours": cumulative_hours,
                "cumulative_cost": round(cumulative_cost, 2),
                "rationale": f"Step {idx}: Target {rec['gap_severity']} gap in {rec['primary_skill']} ({rec['duration_hours']} hrs, ${rec['cost']:,.2f})."
            })

        return {
            "employee_id": emp.id,
            "employee_name": emp.name,
            "department": emp.department,
            "role_title": emp.role.title,
            "total_missing_skills": len(missing_skills),
            "feasible_count": len(feasible_recommendations),
            "rejected_count": len(rejected_recommendations),
            "recommendations": feasible_recommendations,
            "rejected_recommendations": rejected_recommendations,
            "learning_pathway": learning_pathway,
            "total_pathway_cost": round(cumulative_cost, 2),
            "total_pathway_hours": cumulative_hours
        }
