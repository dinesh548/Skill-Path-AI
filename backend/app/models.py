from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Numeric, Boolean, Date, DateTime,
    ForeignKey, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(32), primary_key=True)  # e.g., ROL-000001
    title = Column(String(128), nullable=False)
    department = Column(String(64), nullable=False)
    level = Column(String(32), nullable=False)  # Junior, Mid, Senior, Lead, Principal
    next_role_id = Column(String(32), ForeignKey("roles.id"), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    employees = relationship("Employee", back_populates="role")
    skill_targets = relationship("RoleSkillTarget", back_populates="role", cascade="all, delete-orphan")
    next_role = relationship("Role", remote_side=[id])

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(32), primary_key=True)  # SKL-000001
    name = Column(String(128), unique=True, nullable=False)
    category = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    min_proficiency = Column(Integer, default=0, nullable=False)
    max_proficiency = Column(Integer, default=5, nullable=False)

    # Relationships
    role_targets = relationship("RoleSkillTarget", back_populates="skill")
    employee_skills = relationship("EmployeeSkill", back_populates="skill")
    course_skills = relationship("CourseSkill", back_populates="skill")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(32), primary_key=True)  # EMP-000001
    name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    department = Column(String(64), nullable=False)
    role_id = Column(String(32), ForeignKey("roles.id"), nullable=False)
    hire_date = Column(Date, nullable=False)
    status = Column(String(32), default="ACTIVE", nullable=False)  # ACTIVE, ON_LEAVE, TERMINATED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="employees")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="employee", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionRecord", back_populates="employee")

class RoleSkillTarget(Base):
    __tablename__ = "role_skill_targets"

    id = Column(String(64), primary_key=True)  # RST-<role_id>-<skill_id>
    role_id = Column(String(32), ForeignKey("roles.id"), nullable=False)
    skill_id = Column(String(32), ForeignKey("skills.id"), nullable=False)
    target_proficiency = Column(Integer, nullable=False)  # 1 to 5
    importance_weight = Column(Float, default=1.0, nullable=False)  # 0.5 to 2.0
    is_mandatory = Column(Boolean, default=True, nullable=False)
    effective_date = Column(Date, default=date.today, nullable=False)

    __table_args__ = (
        CheckConstraint("target_proficiency >= 1 AND target_proficiency <= 5", name="check_role_target_proficiency"),
        UniqueConstraint("role_id", "skill_id", name="uq_role_skill"),
    )

    # Relationships
    role = relationship("Role", back_populates="skill_targets")
    skill = relationship("Skill", back_populates="role_targets")

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(String(64), primary_key=True)  # ESK-<emp_id>-<skill_id>
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=False)
    skill_id = Column(String(32), ForeignKey("skills.id"), nullable=False)
    current_proficiency = Column(Integer, default=0, nullable=False)  # 0 to 5
    last_assessed_date = Column(Date, default=date.today, nullable=False)
    assessment_type = Column(String(64), default="INITIAL", nullable=False)  # INITIAL, POST_COURSE, ANNUAL_REVIEW
    verified_by = Column(String(64), default="System", nullable=True)

    __table_args__ = (
        CheckConstraint("current_proficiency >= 0 AND current_proficiency <= 5", name="check_emp_current_proficiency"),
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

class Course(Base):
    __tablename__ = "courses"

    id = Column(String(32), primary_key=True)  # CRS-000001
    title = Column(String(255), nullable=False)
    provider = Column(String(128), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    duration_hours = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    enrolled_count = Column(Integer, default=0, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(32), default="AVAILABLE", nullable=False)  # AVAILABLE, IN_PROGRESS, COMPLETED, CANCELLED
    description = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("cost >= 0", name="check_course_cost_positive"),
        CheckConstraint("duration_hours > 0", name="check_course_duration_positive"),
        CheckConstraint("capacity > 0", name="check_course_capacity_positive"),
        CheckConstraint("end_date >= start_date", name="check_course_dates_order"),
    )

    # Relationships
    skills_taught = relationship("CourseSkill", back_populates="course", cascade="all, delete-orphan")
    prerequisites = relationship(
        "Prerequisite",
        foreign_keys="[Prerequisite.course_id]",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    dependent_courses = relationship(
        "Prerequisite",
        foreign_keys="[Prerequisite.prerequisite_course_id]",
        back_populates="prerequisite_course"
    )
    enrollments = relationship("Enrollment", back_populates="course")

class CourseSkill(Base):
    __tablename__ = "course_skills"

    id = Column(String(64), primary_key=True)  # CSK-<course_id>-<skill_id>
    course_id = Column(String(32), ForeignKey("courses.id"), nullable=False)
    skill_id = Column(String(32), ForeignKey("skills.id"), nullable=False)
    proficiency_gain = Column(Integer, default=1, nullable=False)  # 1 to 3
    target_level_taught = Column(Integer, default=3, nullable=False)  # 1 to 5

    __table_args__ = (
        CheckConstraint("proficiency_gain >= 1 AND proficiency_gain <= 5", name="check_course_proficiency_gain"),
        CheckConstraint("target_level_taught >= 1 AND target_level_taught <= 5", name="check_course_target_level"),
        UniqueConstraint("course_id", "skill_id", name="uq_course_skill"),
    )

    # Relationships
    course = relationship("Course", back_populates="skills_taught")
    skill = relationship("Skill", back_populates="course_skills")

class Prerequisite(Base):
    __tablename__ = "prerequisites"

    id = Column(String(64), primary_key=True)  # PRQ-<course_id>-<prereq_id>
    course_id = Column(String(32), ForeignKey("courses.id"), nullable=False)
    prerequisite_course_id = Column(String(32), ForeignKey("courses.id"), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("course_id != prerequisite_course_id", name="check_no_self_prerequisite"),
        UniqueConstraint("course_id", "prerequisite_course_id", name="uq_course_prerequisite"),
    )

    # Relationships
    course = relationship("Course", foreign_keys=[course_id], back_populates="prerequisites")
    prerequisite_course = relationship("Course", foreign_keys=[prerequisite_course_id], back_populates="dependent_courses")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String(64), primary_key=True)  # ENR-<employee-id>-<course-id>
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=False)
    course_id = Column(String(32), ForeignKey("courses.id"), nullable=False)
    enrollment_date = Column(Date, default=date.today, nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)  # PENDING, APPROVED, IN_PROGRESS, COMPLETED, CANCELLED, REJECTED
    approved_by = Column(String(64), nullable=True)
    approval_date = Column(Date, nullable=True)
    cost_charged = Column(Numeric(10, 2), default=0.00, nullable=False)

    __table_args__ = (
        UniqueConstraint("employee_id", "course_id", name="uq_employee_course_enrollment"),
    )

    # Relationships
    employee = relationship("Employee", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    completion = relationship("Completion", back_populates="enrollment", uselist=False, cascade="all, delete-orphan")

class Completion(Base):
    __tablename__ = "completions"

    id = Column(String(64), primary_key=True)  # CMP-2026-000001
    enrollment_id = Column(String(64), ForeignKey("enrollments.id"), unique=True, nullable=False)
    completion_date = Column(Date, default=date.today, nullable=False)
    assessment_score = Column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00
    reassessment_done = Column(Boolean, default=False, nullable=False)
    previous_proficiency = Column(Integer, nullable=True)
    new_proficiency = Column(Integer, nullable=True)
    skill_improvement = Column(Integer, default=0, nullable=False)
    certificate_url = Column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("assessment_score >= 0.00 AND assessment_score <= 100.00", name="check_assessment_score_range"),
    )

    # Relationships
    enrollment = relationship("Enrollment", back_populates="completion")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(64), primary_key=True)  # BUD-<department>-2026
    department = Column(String(64), unique=True, nullable=False)
    fiscal_year = Column(Integer, default=2026, nullable=False)
    allocated_amount = Column(Numeric(12, 2), nullable=False)
    spent_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    remaining_balance = Column(Numeric(12, 2), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("allocated_amount >= 0", name="check_budget_allocated_positive"),
        CheckConstraint("spent_amount >= 0", name="check_budget_spent_positive"),
    )

class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    issue_id = Column(String(32), primary_key=True)  # ISS-000001
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=True)
    course_id = Column(String(32), ForeignKey("courses.id"), nullable=True)
    issue_type = Column(String(64), nullable=False)  # PREREQUISITE_VIOLATION, BUDGET_EXCEEDED, DUPLICATE_COMPLETION, UNASSESSED_GAP, COURSE_UNAVAILABLE
    severity = Column(String(32), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    detection_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolution_status = Column(String(32), default="OPEN", nullable=False)  # OPEN, RESOLVED, ACKNOWLEDGED, SUPPRESSED
    notes = Column(Text, nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="exceptions")
    course = relationship("Course")
