# SkillPath AI – Comprehensive Data Dictionary

This document details every table and attribute in the SkillPath AI platform, defining technical specifications, domain constraints, and business rules.

---

## 1. Table: `employees`
Stores workforce demographic and organizational profile data.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(32) | NO | PK | Unique Employee Identifier | `EMP-000001` | Immutable reference for workforce audits |
| `name` | VARCHAR(128) | NO | - | Full legal name | `Alex Mercer` | Human readable identification |
| `email` | VARCHAR(128) | NO | UNIQUE | Corporate email | `alex.mercer.1@enterprise.com` | Notification and authentication handle |
| `department` | VARCHAR(64) | NO | - | Department grouping | `Engineering` | Governs departmental budget deduction |
| `role_id` | VARCHAR(32) | NO | FK -> `roles.id` | Current assigned role | `ROL-000002` | Dictates target skill requirements |
| `hire_date` | DATE | NO | - | Employment start date | `2023-04-12` | Tenure calculation |
| `status` | VARCHAR(32) | NO | IN ('ACTIVE', 'ON_LEAVE', 'TERMINATED') | Lifecycle status | `ACTIVE` | Only ACTIVE employees receive recommendations |
| `created_at` | DATETIME | NO | DEFAULT NOW() | Record creation timestamp | `2026-01-01 08:00:00` | Audit traceability |
| `updated_at` | DATETIME | NO | DEFAULT NOW() | Last modification timestamp | `2026-01-01 08:00:00` | Audit traceability |

---

## 2. Table: `roles`
Stores standard job definitions and hierarchical career tracks.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(32) | NO | PK | Role code | `ROL-000001` | Standard career classification |
| `title` | VARCHAR(128) | NO | - | Official job title | `Junior Software Engineer` | Display label on career trees |
| `department` | VARCHAR(64) | NO | - | Business unit | `Engineering` | Organizational alignment |
| `level` | VARCHAR(32) | NO | IN ('Junior', 'Mid', 'Senior', 'Lead', 'Principal') | Career ladder level | `Junior` | Career progression hierarchy |
| `next_role_id` | VARCHAR(32) | YES | FK -> `roles.id` | Direct promotional target | `ROL-000002` | Defines primary career pathway |
| `description` | TEXT | YES | - | Role responsibilities | `Responsible for engineering...` | Guidance for employees |

---

## 3. Table: `skills`
Master catalog of technical, cloud, data, quality, and managerial competencies.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(32) | NO | PK | Skill identifier | `SKL-000001` | Canonical skill reference |
| `name` | VARCHAR(128) | NO | UNIQUE | Standard skill name | `Python` | Core competency keyword |
| `category` | VARCHAR(64) | NO | - | Domain taxonomy | `Programming` | Aggregation category for gap analysis |
| `description` | TEXT | YES | - | Skill scope and rubric | `Competency in Python...` | Evaluation guidance |
| `min_proficiency`| INT | NO | DEFAULT 0 | Lowest rating | `0` | Unassessed or no competency |
| `max_proficiency`| INT | NO | DEFAULT 5 | Highest rating | `5` | Expert or subject matter mastery |

---

## 4. Table: `role_skill_targets`
Defines benchmark competency requirements for job roles.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Unique target ID | `RST-ROL-000001-SKL-000001` | Immutable target association |
| `role_id` | VARCHAR(32) | NO | FK -> `roles.id` | Target role | `ROL-000001` | Role being benchmarked |
| `skill_id` | VARCHAR(32) | NO | FK -> `skills.id` | Required skill | `SKL-000001` | Target skill |
| `target_proficiency`| INT | NO | BETWEEN 1 AND 5 | Required proficiency | `3` | Expected competency level |
| `importance_weight`| FLOAT | NO | 0.5 to 2.0 | Multiplier | `1.5` | Scales recommendation priority |
| `is_mandatory` | BOOLEAN | NO | DEFAULT TRUE | Mandatory gate | `TRUE` | Required for promotion qualification |
| `effective_date` | DATE | NO | - | Start of validity | `2026-01-01` | Versioning of expectations |

---

## 5. Table: `employee_skills`
Records verified employee competency assessments.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Assessment record ID | `ESK-EMP-000001-SKL-000001` | Immutable assessment association |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.id` | Evaluated employee | `EMP-000001` | Individual learner |
| `skill_id` | VARCHAR(32) | NO | FK -> `skills.id` | Evaluated skill | `SKL-000001` | Skill evaluated |
| `current_proficiency`| INT | NO | BETWEEN 0 AND 5 | Assessed level | `2` | Source value for Gap calculation |
| `last_assessed_date` | DATE | NO | - | Date evaluated | `2026-01-10` | Freshness of evaluation |
| `assessment_type`| VARCHAR(64) | NO | - | Evaluation mechanism | `POST_COURSE` | Traceability of proficiency origin |
| `verified_by` | VARCHAR(64) | YES | - | Assessor identity | `Lead Assessor` | Accountability |

---

## 6. Table: `courses`
Accredited courses, bootcamps, and certification curricula.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(32) | NO | PK | Course code | `CRS-000001` | Catalog identifier |
| `title` | VARCHAR(255) | NO | - | Course title | `Python Mastery: Practical Skills`| Display name |
| `provider` | VARCHAR(128) | NO | - | Vendor | `SkillPath Academy` | Quality and provider filtering |
| `cost` | DECIMAL(10,2) | NO | >= 0 | Course tuition | `450.00` | Checked against department budget |
| `duration_hours`| INT | NO | > 0 | Instructional hours | `32` | Learner time commitment |
| `capacity` | INT | NO | > 0 | Maximum seats | `30` | Ceiling on enrollments |
| `enrolled_count`| INT | NO | >= 0 | Reserved seats | `12` | Checked against capacity (Seats left) |
| `start_date` | DATE | NO | - | Schedule start | `2026-02-01` | Planning window constraint |
| `end_date` | DATE | NO | >= start_date | Schedule end | `2026-05-31` | Planning window constraint |
| `status` | VARCHAR(32) | NO | IN ('AVAILABLE', 'IN_PROGRESS', 'EXPIRED') | Status | `AVAILABLE` | Excludes unavailable courses |
| `description` | TEXT | YES | - | Syllabus summary | `Hands-on training...` | Catalog overview |

---

## 7. Table: `course_skills`
Curriculum bridge table linking courses to target skill improvements.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Bridge ID | `CSK-CRS-000001-SKL-000001` | Unique mapping reference |
| `course_id` | VARCHAR(32) | NO | FK -> `courses.id` | Course | `CRS-000001` | Source course |
| `skill_id` | VARCHAR(32) | NO | FK -> `skills.id` | Taught skill | `SKL-000001` | Skill addressed |
| `proficiency_gain`| INT | NO | 1 to 3 | Expected upgrade | `2` | Potential level jump after reassessment |
| `target_level_taught`| INT| NO | 1 to 5 | Target level taught | `4` | Curriculum depth |

---

## 8. Table: `prerequisites`
Directed dependency graph enforcing prerequisite sequences.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Prerequisite link | `PRQ-CRS-000002-CRS-000001` | Unique dependency record |
| `course_id` | VARCHAR(32) | NO | FK -> `courses.id` | Advanced course | `CRS-000002` | Blocked until prereq completed |
| `prerequisite_course_id`| VARCHAR(32)| NO | FK -> `courses.id` | Foundational course | `CRS-000001` | Must appear in completed courses |
| `is_mandatory` | BOOLEAN | NO | DEFAULT TRUE | Mandatory flag | `TRUE` | Violation triggers Exception Case 1 |

---

## 9. Table: `enrollments`
Manages the registration and approval lifecycle state machine.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Unique enrollment code | `ENR-EMP-000001-CRS-000005` | Follows `ENR-<emp>-<crs>` convention |
| `employee_id` | VARCHAR(32) | NO | FK -> `employees.id` | Enrolled learner | `EMP-000001` | Target employee |
| `course_id` | VARCHAR(32) | NO | FK -> `courses.id` | Enrolled course | `CRS-000005` | Target course |
| `enrollment_date`| DATE | NO | - | Submission date | `2026-01-20` | Chronological audit trail |
| `status` | VARCHAR(32) | NO | IN ('PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'REJECTED') | Lifecycle stage | `APPROVED` | Lifecycle workflow state |
| `approved_by` | VARCHAR(64) | YES | - | Approving manager | `Dept Manager` | Financial authority accountability |
| `approval_date` | DATE | YES | - | Date authorized | `2026-01-22` | Audit timestamp |
| `cost_charged` | DECIMAL(10,2)| NO | DEFAULT 0.00 | Charged fee | `450.00` | Real-time budget deduction |

---

## 10. Table: `completions`
Records verified completions, test scores, and formal skill reassessments.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Completion certificate code | `CMP-2026-000001` | Follows `CMP-2026-XXXXXX` convention |
| `enrollment_id` | VARCHAR(64) | NO | UNIQUE, FK -> `enrollments.id` | Enrollment reference | `ENR-EMP-000001-CRS-000005` | Exactly one completion per enrollment |
| `completion_date`| DATE | NO | - | Date finished | `2026-02-14` | Milestone timestamp |
| `assessment_score`| DECIMAL(5,2)| NO| 0.00 to 100.00 | Examination score | `88.50` | Must be >= 70.0% for proficiency upgrade |
| `reassessment_done`| BOOLEAN | NO | DEFAULT FALSE | Reassessment gate | `TRUE` | Only update proficiency when TRUE |
| `previous_proficiency`| INT | YES | NULLABLE | Pre-course level | `2` | Baseline for Skill Improvement |
| `new_proficiency` | INT | YES | NULLABLE | Post-reassessment level | `4` | Upgraded skill rating |
| `skill_improvement`| INT | NO | DEFAULT 0 | Net level gain | `2` | `New Proficiency - Previous Proficiency` |
| `certificate_url` | VARCHAR(255)| YES| - | Verified credential URL | `https://certs.skillpath.ai/...` | Cryptographic evidence link |

---

## 11. Table: `budgets`
Tracks departmental training fund allocations, expenditures, and available balances.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | PK | Budget ID | `BUD-ENGINEERING-2026` | Follows `BUD-<dept>-2026` convention |
| `department` | VARCHAR(64) | NO | UNIQUE | Business unit | `Engineering` | Aligned with Employee.department |
| `fiscal_year` | INT | NO | DEFAULT 2026 | Active fiscal year | `2026` | Accounting fiscal period |
| `allocated_amount`| DECIMAL(12,2)| NO | >= 0 | Authorized cap | `350000.00` | Maximum spend allowed |
| `spent_amount` | DECIMAL(12,2)| NO | >= 0 | Consumed to date | `124987.00` | Sum of approved enrollment costs |
| `remaining_balance`| DECIMAL(12,2)| NO| - | Available capital | `225013.00` | Reconciles: Allocated - Spent |
| `last_updated` | DATETIME | NO | DEFAULT NOW() | Timestamp | `2026-02-16 10:00:00` | Balance update freshness |

---

## 12. Table: `exceptions`
Audit log recording every intercepted edge-case and exceptional decision state.

| Field Name | Type | Nullable | Key / Constraint | Description | Example Value | Business Significance |
|---|---|---|---|---|---|---|
| `issue_id` | VARCHAR(32) | NO | PK | Incident code | `ISS-000001` | Sequential issue tracking ID |
| `employee_id` | VARCHAR(32) | YES | FK -> `employees.id` | Affected employee | `EMP-000001` | Contextual party |
| `course_id` | VARCHAR(32) | YES | FK -> `courses.id` | Affected course | `CRS-000012` | Contextual course |
| `issue_type` | VARCHAR(64) | NO | Enum of 5 Cases | Exception category | `PREREQUISITE_VIOLATION` | Identifies rule breached |
| `severity` | VARCHAR(32) | NO | IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') | Urgency | `HIGH` | Triaging priority |
| `expected_result`| TEXT | NO | - | Rule specification | `Block recommendation...` | Benchmark standard |
| `actual_result` | TEXT | NO | - | Intercepted outcome | `Recommendation blocked` | Evidence of compliance |
| `detection_date` | DATETIME | NO | DEFAULT NOW() | Discovery timestamp | `2026-02-16 10:00:00` | Audit trail |
| `resolution_status`| VARCHAR(32)| NO | IN ('OPEN', 'RESOLVED', 'ACKNOWLEDGED', 'SUPPRESSED') | State | `OPEN` | Lifecycle governance |
| `notes` | TEXT | YES | - | Remediation notes | `Prerequisite course...` | Human reviewer comments |
