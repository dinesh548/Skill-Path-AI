from typing import List, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

# Role schemas
class RoleBase(BaseModel):
    id: str
    title: str
    department: str
    level: str
    next_role_id: Optional[str] = None
    description: Optional[str] = None

class RoleOut(RoleBase):
    model_config = {"from_attributes": True}

# Skill schemas
class SkillBase(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    min_proficiency: int = 0
    max_proficiency: int = 5

class SkillOut(SkillBase):
    model_config = {"from_attributes": True}

# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    email: str
    department: str
    role_id: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeOut(BaseModel):
    id: str
    name: str
    email: str
    department: str
    role_id: str
    role_title: Optional[str] = None
    role_level: Optional[str] = None
    hire_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# EmployeeSkill schemas
class EmployeeSkillOut(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    current_proficiency: int
    last_assessed_date: date
    assessment_type: str
    verified_by: Optional[str] = None

    model_config = {"from_attributes": True}

# Course schemas
class CourseSkillOut(BaseModel):
    skill_id: str
    skill_name: str
    proficiency_gain: int
    target_level_taught: int

class PrerequisiteOut(BaseModel):
    prerequisite_course_id: str
    title: str
    is_mandatory: bool

class CourseOut(BaseModel):
    id: str
    title: str
    provider: str
    cost: float
    duration_hours: int
    capacity: int
    enrolled_count: int
    start_date: date
    end_date: date
    status: str
    description: Optional[str] = None
    skills_taught: List[CourseSkillOut] = []
    prerequisites: List[PrerequisiteOut] = []

    model_config = {"from_attributes": True}

# Enrollment schemas
class EnrollmentCreate(BaseModel):
    employee_id: str
    course_id: str
    auto_approve: bool = False

class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None
    approved_by: Optional[str] = None

class EnrollmentOut(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    course_id: str
    course_title: Optional[str] = None
    enrollment_date: date
    status: str
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
    cost_charged: float
    completion_id: Optional[str] = None
    assessment_score: Optional[float] = None
    reassessment_done: Optional[bool] = None

    model_config = {"from_attributes": True}

# Completion schemas
class CompletionCreate(BaseModel):
    enrollment_id: str
    assessment_score: float = Field(..., ge=0.0, le=100.0)
    completion_date: Optional[date] = None

class CompletionOut(BaseModel):
    id: str
    enrollment_id: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    course_id: Optional[str] = None
    course_title: Optional[str] = None
    completion_date: date
    assessment_score: float
    reassessment_done: bool
    previous_proficiency: Optional[int] = None
    new_proficiency: Optional[int] = None
    skill_improvement: int
    certificate_url: Optional[str] = None

    model_config = {"from_attributes": True}

# Reassessment request
class ReassessmentRequest(BaseModel):
    verified_by: Optional[str] = "Lead Assessor"

# Budget schemas
class BudgetOut(BaseModel):
    id: str
    department: str
    fiscal_year: int
    allocated_amount: float
    spent_amount: float
    remaining_balance: float
    utilization_pct: float
    last_updated: datetime

    model_config = {"from_attributes": True}

# Exception schemas
class ExceptionOut(BaseModel):
    issue_id: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    department: Optional[str] = None
    course_id: Optional[str] = None
    course_title: Optional[str] = None
    issue_type: str
    severity: str
    expected_result: str
    actual_result: str
    detection_date: str
    resolution_status: str
    notes: Optional[str] = None

class ExceptionResolveRequest(BaseModel):
    resolution_status: str  # OPEN, RESOLVED, ACKNOWLEDGED, SUPPRESSED
    notes: Optional[str] = None

# Recommendation schemas
class RecommendationGenerateRequest(BaseModel):
    employee_id: str
    planning_date: Optional[date] = None
