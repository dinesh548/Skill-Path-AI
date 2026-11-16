from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app import models

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_evaluation_metrics(self) -> Dict[str, Any]:
        """
        Calculates all 10 measurable enterprise evaluation metrics directly from source database records.
        """
        # 1. Total skill gaps identified
        # For all employees, compare role_skill_targets to employee_skills
        all_emps = self.db.query(models.Employee).all()
        total_gaps_identified = 0
        total_gap_magnitude = 0

        for emp in all_emps:
            targets = self.db.query(models.RoleSkillTarget).filter(
                models.RoleSkillTarget.role_id == emp.role_id
            ).all()
            skills_map = {es.skill_id: es.current_proficiency for es in emp.skills}
            for t in targets:
                cur = skills_map.get(t.skill_id, 0)
                gap = max(0, t.target_proficiency - cur)
                if gap > 0:
                    total_gaps_identified += 1
                    total_gap_magnitude += gap

        # 2. Skill gaps closed after reassessment
        # Count completions where reassessment_done=True and skill_improvement > 0
        reassessed_completions = self.db.query(models.Completion).filter(
            models.Completion.reassessment_done == True,
            models.Completion.skill_improvement > 0
        ).all()
        gaps_closed_count = len(reassessed_completions)

        # 3. Employee skill improvement percentage
        # Skill Improvement = (New Proficiency - Previous Proficiency)
        all_reassessed = self.db.query(models.Completion).filter(
            models.Completion.reassessment_done == True
        ).all()
        total_improvement_points = sum(c.skill_improvement for c in all_reassessed)
        avg_skill_improvement = (
            round(total_improvement_points / len(all_reassessed), 2) if all_reassessed else 0.0
        )
        skill_improvement_pct = (
            round((total_improvement_points / (len(all_reassessed) * 5.0)) * 100, 1) if all_reassessed else 0.0
        )

        # 4. Course completion rate
        # Formula: Completion Rate = (Completed Enrollments / Eligible Enrollments) * 100
        total_enrollments = self.db.query(models.Enrollment).count()
        completed_enrollments = self.db.query(models.Enrollment).filter(
            models.Enrollment.status == "COMPLETED"
        ).count()
        eligible_enrollments = self.db.query(models.Enrollment).filter(
            models.Enrollment.status.in_(["COMPLETED", "IN_PROGRESS", "APPROVED"])
        ).count()
        completion_rate = (
            round((completed_enrollments / eligible_enrollments * 100), 1) if eligible_enrollments > 0 else 0.0
        )

        # 5. Department budget utilization
        # Formula: Budget Utilization = (Total Spent / Total Budget) * 100
        budgets = self.db.query(models.Budget).all()
        total_allocated = sum(float(b.allocated_amount) for b in budgets)
        total_spent = sum(float(b.spent_amount) for b in budgets)
        total_remaining = sum(float(b.remaining_balance) for b in budgets)
        budget_utilization_pct = (
            round((total_spent / total_allocated * 100), 1) if total_allocated > 0 else 0.0
        )

        # 6. Recommendation acceptance rate
        # Enrollments approved or in progress vs total enrollments
        accepted_enrollments = self.db.query(models.Enrollment).filter(
            models.Enrollment.status.in_(["APPROVED", "IN_PROGRESS", "COMPLETED"])
        ).count()
        recommendation_acceptance_rate = (
            round((accepted_enrollments / total_enrollments * 100), 1) if total_enrollments > 0 else 0.0
        )

        # 7. Prerequisite violation count
        prereq_violations = self.db.query(models.ExceptionRecord).filter(
            models.ExceptionRecord.issue_type == "PREREQUISITE_VIOLATION"
        ).count()

        # 8. Duplicate completion count
        duplicate_completions = self.db.query(models.ExceptionRecord).filter(
            models.ExceptionRecord.issue_type == "DUPLICATE_COMPLETION"
        ).count()

        # 9. Infeasible recommendation count (budget exceeded or course unavailable)
        infeasible_recommendations = self.db.query(models.ExceptionRecord).filter(
            models.ExceptionRecord.issue_type.in_(["BUDGET_EXCEEDED", "COURSE_UNAVAILABLE"])
        ).count()

        # 10. Average learning duration
        # Average duration_hours of completed courses
        completed_course_durations = (
            self.db.query(models.Course.duration_hours)
            .join(models.Enrollment, models.Enrollment.course_id == models.Course.id)
            .filter(models.Enrollment.status == "COMPLETED")
            .all()
        )
        avg_learning_duration = (
            round(sum(d[0] for d in completed_course_durations) / len(completed_course_durations), 1)
            if completed_course_durations else 0.0
        )

        return {
            "metrics": [
                {
                    "metric_id": "MTR-01",
                    "name": "Total Skill Gaps Identified",
                    "value": total_gaps_identified,
                    "unit": "gaps",
                    "formula": "COUNT(Role Target - Current Proficiency > 0)",
                    "detail": f"{total_gaps_identified} specific skill shortages identified across {len(all_emps)} active employees (Total gap points: {total_gap_magnitude})."
                },
                {
                    "metric_id": "MTR-02",
                    "name": "Skill Gaps Closed After Reassessment",
                    "value": gaps_closed_count,
                    "unit": "skills",
                    "formula": "COUNT(Reassessment Done = TRUE AND Skill Improvement > 0)",
                    "detail": f"{gaps_closed_count} skill proficiencies officially upgraded post-course examination."
                },
                {
                    "metric_id": "MTR-03",
                    "name": "Employee Skill Improvement",
                    "value": avg_skill_improvement,
                    "unit": "levels (avg)",
                    "percentage": skill_improvement_pct,
                    "formula": "AVG(New Proficiency - Previous Proficiency)",
                    "detail": f"Average verified competency gain of +{avg_skill_improvement} proficiency levels per completed course reassessment ({skill_improvement_pct}% scale improvement)."
                },
                {
                    "metric_id": "MTR-04",
                    "name": "Course Completion Rate",
                    "value": completion_rate,
                    "unit": "%",
                    "formula": "(Completed Enrollments / Eligible Enrollments) * 100",
                    "detail": f"{completed_enrollments} completions out of {eligible_enrollments} active learners ({completion_rate}%)."
                },
                {
                    "metric_id": "MTR-05",
                    "name": "Department Budget Utilization",
                    "value": budget_utilization_pct,
                    "unit": "%",
                    "formula": "(Total Spent / Total Budget) * 100",
                    "detail": f"${total_spent:,.2f} utilized of ${total_allocated:,.2f} total annual allocation (${total_remaining:,.2f} remaining balance)."
                },
                {
                    "metric_id": "MTR-06",
                    "name": "Recommendation Acceptance Rate",
                    "value": recommendation_acceptance_rate,
                    "unit": "%",
                    "formula": "(Approved or Completed / Total Enrollments) * 100",
                    "detail": f"{accepted_enrollments} approved out of {total_enrollments} total requests ({recommendation_acceptance_rate}%)."
                },
                {
                    "metric_id": "MTR-07",
                    "name": "Prerequisite Violations Intercepted",
                    "value": prereq_violations,
                    "unit": "exceptions",
                    "formula": "COUNT(Exception Type = 'PREREQUISITE_VIOLATION')",
                    "detail": f"{prereq_violations} illegal enrollment attempts blocked by prerequisite engine."
                },
                {
                    "metric_id": "MTR-08",
                    "name": "Duplicate Completions Prevented",
                    "value": duplicate_completions,
                    "unit": "exceptions",
                    "formula": "COUNT(Exception Type = 'DUPLICATE_COMPLETION')",
                    "detail": f"{duplicate_completions} duplicate completion submissions safely intercepted without history loss."
                },
                {
                    "metric_id": "MTR-09",
                    "name": "Infeasible Recommendations Filtered",
                    "value": infeasible_recommendations,
                    "unit": "exceptions",
                    "formula": "COUNT(Exception Type IN ('BUDGET_EXCEEDED', 'COURSE_UNAVAILABLE'))",
                    "detail": f"{infeasible_recommendations} candidates rejected upfront due to budget depletion or scheduling expiration."
                },
                {
                    "metric_id": "MTR-10",
                    "name": "Average Learning Duration",
                    "value": avg_learning_duration,
                    "unit": "hours",
                    "formula": "AVG(Course Duration for Completed Enrollments)",
                    "detail": f"{avg_learning_duration} curriculum hours average per completed employee training pathway."
                }
            ],
            "budget_summary": {
                "total_allocated": total_allocated,
                "total_spent": total_spent,
                "total_remaining": total_remaining,
                "utilization_pct": budget_utilization_pct
            },
            "enrollment_summary": {
                "total": total_enrollments,
                "completed": completed_enrollments,
                "eligible": eligible_enrollments,
                "completion_rate": completion_rate
            }
        }
