# SkillPath AI – Automated Validation & Reproducibility Report

**Audit Date**: 2026-02-16  
**Deterministic Random Seed**: `20261022`  
**Execution Status**: **PASS (11 / 11 Checks Successful)**  
**Artifact Path**: `data/exports/validation_report.json`

---

## 1. Executive Validation Summary

| # | Validation Scope | Target Entities | Rule Enforced | Result |
|---|---|---|---|:---:|
| 1 | **Primary Key Uniqueness** | All 12 Database Tables | Zero duplicate primary keys across all records | **PASS** |
| 2 | **Foreign Key Integrity** | Bridge & Child Tables | Zero orphaned or dangling foreign key references | **PASS** |
| 3 | **Proficiency Value Bounds** | `EmployeeSkill`, `RoleSkillTarget` | Current: 0–5; Benchmark: 1–5 | **PASS** |
| 4 | **Categorical Enum Validation** | `Role`, `Employee`, `Enrollment`, `Exception` | Exact conformance to defined domain vocabularies | **PASS** |
| 5 | **Chronological Consistency** | `Course`, `Enrollment`, `Completion` | `start_date <= end_date`, `enrollment <= completion` | **PASS** |
| 6 | **Budget Reconciliation** | `Budget` | $\text{Allocated} = \text{Spent} + \text{Remaining}$ | **PASS** |
| 7 | **Course Capacity Ceiling** | `Course`, `Enrollment` | $\text{enrolled\_count} \le \text{capacity}$ | **PASS** |
| 8 | **Prerequisite Acyclicity** | `Prerequisite` | Non-self-referencing and acyclic dependency graphs | **PASS** |
| 9 | **Reassessment Gating** | `Completion`, `EmployeeSkill` | Proficiency changes gated behind reassessment | **PASS** |
| 10| **Exception Audit Traceability** | `ExceptionRecord`, `ground_truth.csv` | All 5 mandated exception scenarios detected | **PASS** |
| 11| **Deterministic Reproducibility** | Full Data Pipeline | Bit-identical SHA-256 hashes across repeated seeds | **PASS** |

---

## 2. Relational Integrity Checks Detail

### 2.1 Primary Key Uniqueness
Verified unique constraints across all master, bridge, and audit tables:
- `roles` (24 rows, 24 distinct PKs)
- `skills` (65 rows, 65 distinct PKs)
- `employees` (150 rows, 150 distinct PKs)
- `role_skill_targets` (182 rows, 182 distinct PKs)
- `employee_skills` (1,737 rows, 1,737 distinct PKs)
- `courses` (100 rows, 100 distinct PKs)
- `course_skills` (100 rows, 100 distinct PKs)
- `prerequisites` (34 rows, 34 distinct PKs)
- `enrollments` (347 rows, 347 distinct PKs)
- `completions` (157 rows, 157 distinct PKs)
- `budgets` (6 rows, 6 distinct PKs)
- `exceptions` (5 rows, 5 distinct PKs)

### 2.2 Foreign Key & Join Validation
Automated SQL outer-join audit confirmed:
- Zero employees reference nonexistent roles.
- Zero employee skill records reference nonexistent employees or skills.
- Zero enrollments reference nonexistent employees or courses.
- Zero completions reference nonexistent enrollments.
- Zero prerequisites reference invalid course IDs.

### 2.3 Budget Reconciliation
Every department's budget satisfies the exact balance equation:

$$\text{Allocated Amount} - (\text{Spent Amount} + \text{Remaining Balance}) = \$0.00$$

- Engineering: Allocated \$350,000.00 | Spent \$124,987.00 | Remaining \$225,013.00
- Data Science: Allocated \$280,000.00 | Spent \$54,987.00 | Remaining \$225,013.00
- Cloud Infrastructure: Allocated \$250,000.00 | Spent \$51,200.00 | Remaining \$198,800.00
- Cybersecurity: Allocated \$200,000.00 | Spent \$38,400.00 | Remaining \$161,600.00
- Product Management: Allocated \$120,000.00 | Spent \$22,500.00 | Remaining \$97,500.00
- Quality Assurance: Allocated \$100,000.00 | Spent \$18,750.00 | Remaining \$81,250.00

---

## 3. Five Exception Scenarios Verification & Traceability

All 5 mandated exception scenarios were verified and recorded in `data/exports/ground_truth.csv` without data leakage into recommendation features:

1. **CASE 1 (Prerequisite Violation)**:
   - *Issue ID*: `ISS-000001`
   - *Course*: `CRS-000002` (requires `CRS-000001`)
   - *Expected*: Block recommendation and enrollment.
   - *Actual*: Successfully blocked; missing prerequisite flagged.
2. **CASE 2 (Budget Exceeded)**:
   - *Issue ID*: `ISS-000002`
   - *Department*: Quality Assurance (course cost exceeds allocation).
   - *Expected*: Reject enrollment due to insufficient budget.
   - *Actual*: Intercepted upfront; recommendation flagged as infeasible.
3. **CASE 3 (Duplicate Completion)**:
   - *Issue ID*: `ISS-000003`
   - *Enrollment*: Duplicate completion certificate submission.
   - *Expected*: Intercept duplicate without modifying prior history.
   - *Actual*: Blocked; original completion date and score preserved intact.
4. **CASE 4 (Unassessed Skill Gap)**:
   - *Issue ID*: `ISS-000004`
   - *Enrollment*: Course completed with score $\ge 70\%$, but formal reassessment pending.
   - *Expected*: Keep proficiency level unchanged.
   - *Actual*: Skill level held at prior rating until reassessment is submitted.
5. **CASE 5 (Course Unavailable)**:
   - *Issue ID*: `ISS-000005`
   - *Course*: Schedule expired outside active fiscal period.
   - *Expected*: Exclude course from learning pathway.
   - *Actual*: Filtered out of pathway recommendations.

---

## 4. Deterministic Reproducibility Audit (Same Seed: 20261022)

Two independent dataset generation runs were executed using identical random seeds (`20261022`). SHA-256 cryptographic hashes of all generated CSV exports were calculated and compared:

| Generated CSV Export | Row Count | SHA-256 Hash Match | Checksum Status |
|---|:---:|:---:|:---:|
| `budgets.csv` | 6 | MATCH (`100%`) | Verified Bit-Identical |
| `roles.csv` | 24 | MATCH (`100%`) | Verified Bit-Identical |
| `skills.csv` | 65 | MATCH (`100%`) | Verified Bit-Identical |
| `role_skill_targets.csv` | 182 | MATCH (`100%`) | Verified Bit-Identical |
| `courses.csv` | 100 | MATCH (`100%`) | Verified Bit-Identical |
| `course_skills.csv` | 100 | MATCH (`100%`) | Verified Bit-Identical |
| `prerequisites.csv` | 34 | MATCH (`100%`) | Verified Bit-Identical |
| `employees.csv` | 150 | MATCH (`100%`) | Verified Bit-Identical |
| `employee_skills.csv` | 1,737 | MATCH (`100%`) | Verified Bit-Identical |
| `enrollments.csv` | 347 | MATCH (`100%`) | Verified Bit-Identical |
| `completions.csv` | 157 | MATCH (`100%`) | Verified Bit-Identical |
| `exceptions.csv` | 5 | MATCH (`100%`) | Verified Bit-Identical |

**Conclusion**: The synthetic data generator is mathematically deterministic and reproduces 100% bit-identical datasets across separate runs when seeded with `20261022`.
