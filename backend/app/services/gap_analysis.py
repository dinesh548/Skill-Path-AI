from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app import models

def get_severity(gap: int) -> str:
    if gap <= 0:
        return "Met"
    elif gap == 1:
        return "Low"
    elif gap == 2:
        return "Medium"
    elif gap == 3:
        return "High"
    else:
        return "Critical"

class SkillGapEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_employee_gaps(self, employee_id: str) -> Dict[str, Any]:
        """
        Calculate skill gaps for a single employee based on current role targets.
        Formula: Skill Gap = MAX(0, Required Proficiency - Current Proficiency)
        """
        emp = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not emp:
            return None

        role = emp.role
        role_targets = self.db.query(models.RoleSkillTarget).filter(
            models.RoleSkillTarget.role_id == role.id
        ).all()

        emp_skills_map = {
            es.skill_id: es for es in self.db.query(models.EmployeeSkill).filter(
                models.EmployeeSkill.employee_id == employee_id
            ).all()
        }

        gaps = []
        total_required_points = 0
        total_current_points = 0
        total_gap_points = 0
        missing_skills_count = 0
        critical_gaps_count = 0

        for rt in role_targets:
            skill = rt.skill
            es = emp_skills_map.get(rt.skill_id)
            current_prof = es.current_proficiency if es else 0
            required_prof = rt.target_proficiency
            
            gap = max(0, required_prof - current_prof)
            severity = get_severity(gap)

            if current_prof == 0:
                missing_skills_count += 1
            if gap >= 4 or (gap >= 3 and rt.importance_weight >= 1.5):
                critical_gaps_count += 1

            total_required_points += required_prof
            total_current_points += min(current_prof, required_prof)
            total_gap_points += gap

            proficiency_pct = round((current_prof / required_prof * 100) if required_prof > 0 else 100.0, 1)

            gaps.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "category": skill.category,
                "current_proficiency": current_prof,
                "required_proficiency": required_prof,
                "gap": gap,
                "severity": severity,
                "importance_weight": rt.importance_weight,
                "is_mandatory": rt.is_mandatory,
                "proficiency_pct": min(100.0, proficiency_pct),
                "last_assessed_date": str(es.last_assessed_date) if es else None
            })

        # Sort gaps by gap descending, then importance weight descending
        gaps.sort(key=lambda x: (x["gap"], x["importance_weight"]), reverse=True)

        overall_readiness = round(
            (total_current_points / total_required_points * 100) if total_required_points > 0 else 100.0, 1
        )

        return {
            "employee_id": emp.id,
            "employee_name": emp.name,
            "department": emp.department,
            "role_id": role.id,
            "role_title": role.title,
            "role_level": role.level,
            "total_target_skills": len(role_targets),
            "missing_skills_count": missing_skills_count,
            "critical_gaps_count": critical_gaps_count,
            "total_gap_points": total_gap_points,
            "overall_readiness_pct": overall_readiness,
            "skills": gaps
        }

    def get_department_skill_gaps(self) -> List[Dict[str, Any]]:
        """Department-wise aggregated skill gap metrics."""
        departments = [d[0] for d in self.db.query(models.Employee.department).distinct().all()]
        dept_metrics = []

        for dept in sorted(departments):
            emps = self.db.query(models.Employee).filter(models.Employee.department == dept).all()
            if not emps:
                continue

            dept_total_gaps = 0
            dept_critical_gaps = 0
            dept_readiness_sum = 0

            for emp in emps:
                res = self.calculate_employee_gaps(emp.id)
                if res:
                    dept_total_gaps += res["total_gap_points"]
                    dept_critical_gaps += res["critical_gaps_count"]
                    dept_readiness_sum += res["overall_readiness_pct"]

            avg_readiness = round(dept_readiness_sum / len(emps), 1) if emps else 0.0
            avg_gap_per_emp = round(dept_total_gaps / len(emps), 2) if emps else 0.0

            dept_metrics.append({
                "department": dept,
                "employee_count": len(emps),
                "total_gap_points": dept_total_gaps,
                "avg_gap_per_emp": avg_gap_per_emp,
                "critical_gaps_count": dept_critical_gaps,
                "avg_readiness_pct": avg_readiness
            })

        return dept_metrics

    def get_top_skill_shortages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify top skills with highest cumulative gap points across the organization."""
        # Query all employees and role targets
        all_emps = self.db.query(models.Employee).all()
        skill_totals = {}

        for emp in all_emps:
            role_targets = self.db.query(models.RoleSkillTarget).filter(
                models.RoleSkillTarget.role_id == emp.role_id
            ).all()
            emp_skills = {es.skill_id: es.current_proficiency for es in emp.skills}

            for rt in role_targets:
                cur = emp_skills.get(rt.skill_id, 0)
                gap = max(0, rt.target_proficiency - cur)
                if gap > 0:
                    st = skill_totals.setdefault(rt.skill_id, {
                        "skill_id": rt.skill_id,
                        "skill_name": rt.skill.name,
                        "category": rt.skill.category,
                        "total_gap_points": 0,
                        "affected_employees": 0,
                        "critical_count": 0
                    })
                    st["total_gap_points"] += gap
                    st["affected_employees"] += 1
                    if gap >= 3:
                        st["critical_count"] += 1

        sorted_skills = sorted(skill_totals.values(), key=lambda x: x["total_gap_points"], reverse=True)
        return sorted_skills[:limit]

    def get_role_skill_gaps(self) -> List[Dict[str, Any]]:
        """Role-wise aggregated skill gap analytics."""
        roles = self.db.query(models.Role).all()
        role_metrics = []

        for role in roles:
            emps = self.db.query(models.Employee).filter(models.Employee.role_id == role.id).all()
            if not emps:
                continue

            total_gap = 0
            for emp in emps:
                res = self.calculate_employee_gaps(emp.id)
                if res:
                    total_gap += res["total_gap_points"]

            role_metrics.append({
                "role_id": role.id,
                "title": role.title,
                "department": role.department,
                "level": role.level,
                "employee_count": len(emps),
                "total_gap_points": total_gap,
                "avg_gap_per_emp": round(total_gap / len(emps), 2)
            })

        role_metrics.sort(key=lambda x: x["avg_gap_per_emp"], reverse=True)
        return role_metrics
