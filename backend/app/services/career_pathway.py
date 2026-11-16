from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app import models

class CareerPathwayEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_career_pathway(self, employee_id: str, target_role_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates career progression pathway, missing competencies, roadmap courses,
        estimated cost/duration, and career readiness percentage.
        """
        emp = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not emp:
            return {"error": f"Employee {employee_id} not found"}

        current_role = emp.role

        # Determine target role
        target_role = None
        if target_role_id:
            target_role = self.db.query(models.Role).filter(models.Role.id == target_role_id).first()

        if not target_role:
            # Look at current_role.next_role_id
            if current_role.next_role_id:
                target_role = self.db.query(models.Role).filter(models.Role.id == current_role.next_role_id).first()
            else:
                # If principal / top level, find next highest or same dept
                target_role = current_role

        # Build full role ladder progression in department
        dept_roles = self.db.query(models.Role).filter(models.Role.department == emp.department).all()
        ladder = []
        role_map = {r.id: r for r in dept_roles}
        # Trace roots (roles not referenced by any other next_role_id, or lowest level)
        level_order = {"Junior": 1, "Mid": 2, "Senior": 3, "Lead": 4, "Principal": 5}
        sorted_dept_roles = sorted(dept_roles, key=lambda r: level_order.get(r.level, 3))
        
        for r in sorted_dept_roles:
            ladder.append({
                "role_id": r.id,
                "title": r.title,
                "level": r.level,
                "is_current": (r.id == current_role.id),
                "is_target": (r.id == target_role.id)
            })

        # Calculate requirements for target role
        target_skill_targets = self.db.query(models.RoleSkillTarget).filter(
            models.RoleSkillTarget.role_id == target_role.id
        ).all()

        emp_skills_map = {
            es.skill_id: es.current_proficiency
            for es in self.db.query(models.EmployeeSkill).filter(
                models.EmployeeSkill.employee_id == employee_id
            ).all()
        }

        competencies = []
        total_target_score = 0
        total_emp_score = 0
        missing_skills_count = 0
        gap_skills_for_courses = []

        for rt in target_skill_targets:
            s = rt.skill
            cur_prof = emp_skills_map.get(rt.skill_id, 0)
            req_prof = rt.target_proficiency
            gap = max(0, req_prof - cur_prof)

            total_target_score += req_prof
            total_emp_score += min(cur_prof, req_prof)

            if gap > 0:
                missing_skills_count += 1
                gap_skills_for_courses.append(s.id)

            competencies.append({
                "skill_id": s.id,
                "skill_name": s.name,
                "category": s.category,
                "current_proficiency": cur_prof,
                "target_proficiency": req_prof,
                "gap": gap,
                "status": "MET" if gap == 0 else ("PARTIAL" if cur_prof > 0 else "MISSING"),
                "importance_weight": rt.importance_weight
            })

        career_readiness_pct = round(
            (total_emp_score / total_target_score * 100) if total_target_score > 0 else 100.0, 1
        )

        # Identify courses to bridge the target role gap
        recommended_courses = []
        total_duration = 0
        total_cost = 0.0

        if gap_skills_for_courses:
            course_skills = self.db.query(models.CourseSkill).filter(
                models.CourseSkill.skill_id.in_(gap_skills_for_courses)
            ).all()
            c_ids = {cs.course_id for cs in course_skills}
            courses = self.db.query(models.Course).filter(
                models.Course.id.in_(c_ids),
                models.Course.status == "AVAILABLE"
            ).all()

            # Deduplicate by primary skill to provide a focused roadmap
            covered_skills = set()
            for c in courses:
                taught = [cs.skill_id for cs in c.skills_taught if cs.skill_id in gap_skills_for_courses]
                if taught and not all(sid in covered_skills for sid in taught):
                    skill_name = next(s["skill_name"] for s in competencies if s["skill_id"] == taught[0])
                    recommended_courses.append({
                        "course_id": c.id,
                        "title": c.title,
                        "provider": c.provider,
                        "duration_hours": c.duration_hours,
                        "cost": float(c.cost),
                        "skill_addressed": skill_name
                    })
                    total_duration += c.duration_hours
                    total_cost += float(c.cost)
                    for sid in taught:
                        covered_skills.add(sid)

        return {
            "employee_id": emp.id,
            "employee_name": emp.name,
            "department": emp.department,
            "current_role": {
                "id": current_role.id,
                "title": current_role.title,
                "level": current_role.level
            },
            "target_role": {
                "id": target_role.id,
                "title": target_role.title,
                "level": target_role.level,
                "description": target_role.description
            },
            "career_readiness_pct": career_readiness_pct,
            "total_target_competencies": len(target_skill_targets),
            "missing_competencies_count": missing_skills_count,
            "competency_breakdown": competencies,
            "career_ladder": ladder,
            "recommended_courses": recommended_courses,
            "estimated_learning_hours": total_duration,
            "estimated_total_cost": round(total_cost, 2),
            "summary": f"{emp.name} has achieved {career_readiness_pct}% readiness for {target_role.title}. Bridging {missing_skills_count} competency gaps will require approximately {total_duration} hours of training (${total_cost:,.2f})."
        }
