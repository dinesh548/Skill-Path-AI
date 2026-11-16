# SkillPath AI – Business Rules & Algorithmic Specifications

This document defines the deterministic rules, mathematical formulas, lifecycle transitions, and exception protocols governing the SkillPath AI platform.

---

## 1. Skill Gap Analysis Engine

### 1.1 Fundamental Formula
Skill gap calculations are strictly computed from source relational data. Independent or unanchored gap values are prohibited.

$$\text{Skill Gap} = \max(0, \text{Required Proficiency} - \text{Current Proficiency})$$

### 1.2 Severity Classification Rubric

| Gap Value | Classification | Operational Meaning | Action Policy |
|---|---|---|---|
| **0** | **Met** | Employee meets or exceeds role benchmark | No remediation required |
| **1** | **Low** | Minor gap; manageable via self-paced or peer learning | Recommended for standard training queue |
| **2** | **Medium** | Notable gap; affects delivery efficiency | Prioritized in upcoming quarterly planning |
| **3** | **High** | Significant deficit in mandatory skill | High priority; fast-tracked training enrollment |
| **4 – 5** | **Critical** | Critical shortfall in essential or foundational skill | Immediate escalation; urgent curriculum recommendation |

*Weighting Rule*: When a skill carries an `importance_weight >= 1.5`, a Gap of 3 is automatically elevated to **Critical** severity.

### 1.3 Role Readiness Percentage
The aggregated readiness of an employee for their current role is calculated as:

$$\text{Role Readiness} = \left( \frac{\sum \min(\text{Current Proficiency}_i, \text{Required Proficiency}_i)}{\sum \text{Required Proficiency}_i} \right) \times 100$$

---

## 2. Intelligent Course Recommendation Engine (12-Step Pipeline)

For each active employee, the recommendation engine executes the following deterministic 12-step evaluation pipeline:

```
[1. Current Role] ─────────► [2. Role Skill Benchmarks]
                                       │
[3. Employee Skills] ───────────────────┘
         │
         ▼
[4. Calculate Missing Skills (Gap > 0)]
         │
         ▼
[5. Identify Courses Teaching Missing Skills]
         │
         ├──────────────────────────────────────────────────────┐
         ▼                                                      ▼
[6. Verify Prerequisites] (CASE 1 Gate)               [7. Verify Availability & Dates] (CASE 5 Gate)
         │                                                      │
         ├──────────────────────────────────────────────────────┤
         ▼                                                      ▼
[8. Check Available Seats] (Capacity Gate)            [9. Check Department Budget] (CASE 2 Gate)
         │                                                      │
         └──────────────────────┬───────────────────────────────┘
                                ▼
               [10. Calculate Course Priority Score]
                                │
                                ▼
               [11. Generate Recommendations & Explanations]
                                │
                                ▼
               [12. Build Ordered Learning Pathway Sequence]
```

### 2.1 Candidate Eligibility Gates
A course $C$ is **strictly ineligible** if any of the following gates fail:
1. **Prerequisite Gate (CASE 1)**: All courses $P \in \text{Prerequisites}(C)$ marked `is_mandatory = TRUE` must exist in the employee's verified `completions` records.
2. **Availability Gate (CASE 5)**: Course status must be `AVAILABLE` and $\text{end\_date}(C) \ge \text{planning\_date}$.
3. **Seat Capacity Gate**: Available seats $(\text{capacity} - \text{enrolled\_count}) > 0$.
4. **Budget Gate (CASE 2)**: $\text{cost}(C) \le \text{remaining\_balance}(\text{Department Budget})$.

### 2.2 Priority Scoring Formula
Feasible candidate courses are ranked according to a multi-objective optimization score:

$$\text{Priority Score} = (\text{Severity Base} \times \text{Importance Weight}) + \text{Coverage Bonus} + \text{Efficiency Score}$$

Where:
- $\text{Severity Base}$: Critical = 40.0, High = 30.0, Medium = 20.0, Low = 10.0.
- $\text{Importance Weight}$: $0.5 \le w \le 2.0$ (from `RoleSkillTarget`).
- $\text{Coverage Bonus}$: $(N_{\text{gaps\_covered}} - 1) \times 15.0$ (rewards courses addressing multiple gaps simultaneously).
- $\text{Efficiency Score}$: $\max\left(5.0, 30.0 - \frac{\text{duration\_hours}}{4.0} - \frac{\text{cost}}{150.0}\right)$.

### 2.3 Transparent Explanations
- **Positive Recommendation Explanation**:
  > *"Recommended [Course Title] because the employee has a [Skill Name] proficiency gap of [Gap] (Target: [Req], Current: [Cur]) and meets all prerequisites. The course is available ([Seats] seats remaining) and fits within the [Department] departmental budget ($[Cost] <= $[Remaining])."*
- **Rejected Recommendation Explanation**:
  > *"Rejected [Course Title] because prerequisite [Prerequisite Title] has not been completed."*
  > *"Rejected [Course Title] ($[Cost]) because [Department] department remaining budget ($[Remaining]) is insufficient."*

---

## 3. Five Mandated Exception Scenarios

| Scenario | Trigger Condition | Engine Policy | Traceability Record |
|---|---|---|---|
| **CASE 1: Prerequisite Violation** | Enrollment or recommendation requested for a course whose mandatory prerequisite is not in employee's completed courses. | **Block recommendation and enrollment.** Raise `PREREQUISITE_VIOLATION`. | Log in `exceptions` table with severity `HIGH`. Expected: Block recommendation; Actual: Unsatisfied prerequisite blocked. |
| **CASE 2: Budget Exceeded** | Course tuition fee exceeds department remaining budget balance. | **Reject enrollment.** Flag recommendation as infeasible. Raise `BUDGET_EXCEEDED`. | Log in `exceptions` table with severity `CRITICAL`. Expected: Insufficient funds rejection; Actual: Rejected upfront. |
| **CASE 3: Duplicate Completion** | Completion submission received for an enrollment that already has a verified completion record. | **Intercept duplicate.** Preserve original completion date, score, and certificate history unmodified. Raise `DUPLICATE_COMPLETION`. | Log in `exceptions` table with severity `MEDIUM`. Idempotent rejection; historical record safeguarded. |
| **CASE 4: Unassessed Gap** | Course completed with score $\ge 70\%$, but formal post-course skill examination has not been verified. | **Hold proficiency unchanged.** Keep existing skill level; do not credit automated upgrade. Raise `UNASSESSED_GAP`. | Log in `exceptions` table with severity `HIGH`. Pending reassessment; resolved upon formal assessor submission. |
| **CASE 5: Course Unavailable** | Course status is `EXPIRED` or scheduled dates lie outside the active 2026 fiscal planning window. | **Exclude from recommendation pathway.** Filter out during candidate generation. Raise `COURSE_UNAVAILABLE`. | Log in `exceptions` table with severity `LOW`. Excluded from learning roadmap. |

---

## 4. Learning Lifecycle & Proficiency Update State Machine

The platform strictly enforces the tripartite operational principle:

$$\text{Attendance} \ne \text{Completion} \ne \text{Skill Improvement}$$

### 4.1 Lifecycle States

```
[ PENDING ] ────────► [ REJECTED / CANCELLED ]
     │
     ▼ (Manager Approval + Budget Deduction)
[ APPROVED ] ────────► [ CANCELLED ] (Seat & Budget Refunded)
     │
     ▼ (Course Start)
[ IN_PROGRESS ]
     │
     ▼ (Course Finished + Exam Submitted)
[ COMPLETED ] (reassessment_done = FALSE; Proficiency Unchanged)
     │
     ▼ (Assessor Verification + Score >= 70%)
[ REASSESSED ] (reassessment_done = TRUE; EmployeeSkill Updated)
```

### 4.2 Proficiency Upgrade Rule
- An employee's proficiency in `EmployeeSkill` is updated **only and exclusively** when:
  1. Enrollment status is `COMPLETED`.
  2. Assessment score $\ge 70.0\%$.
  3. Reassessment action is officially submitted by a verified assessor (`reassessment_done = TRUE`).
- When reassessed, the new level is computed as:

$$\text{New Proficiency} = \min(5, \text{Previous Proficiency} + \text{Proficiency Gain})$$
$$\text{Skill Improvement} = \text{New Proficiency} - \text{Previous Proficiency}$$

---

## 5. Department Budget Accounting Rules

1. **Reconciliation Invariant**: For every department budget, the following invariant must hold true at all times:
   $$\text{Allocated Amount} = \text{Spent Amount} + \text{Remaining Balance}$$
2. **Expenditure Commitment**: When an enrollment is `APPROVED`, the department's `spent_amount` increments by `course.cost` and `remaining_balance` decrements by `course.cost`.
3. **Refund on Cancellation**: When an approved or in-progress enrollment is `CANCELLED`, the reserved seat is released and the course cost is immediately credited back to the department's `remaining_balance`.
4. **Budget Utilization Formula**:
   $$\text{Budget Utilization} = \left( \frac{\text{Total Spent}}{\text{Total Budget}} \right) \times 100$$

---

## 6. Career Pathway Progression

1. **Career Readiness Score**:
   $$\text{Career Readiness} = \left( \frac{\sum \min(\text{Current Proficiency}_i, \text{Target Role Proficiency}_i)}{\sum \text{Target Role Proficiency}_i} \right) \times 100$$
2. **Roadmap Generation**: Identifies the specific competencies where $\text{Target Role Proficiency} > \text{Current Proficiency}$, filters active accredited courses addressing those skills, orders them sequentially, and computes cumulative training duration and investment.
