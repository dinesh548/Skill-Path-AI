# SkillPath AI – Source Code Manifest & Architecture Inventory

This manifest details the directory structure, file paths, responsibilities, and implementation status for all components of the SkillPath AI platform.

---

## 1. Directory Tree

```
SkillPath AI
├── .env.example                               # Environment template
├── .gitignore                                  # Git exclusion configuration
├── BUSINESS_RULES.md                          # Business rules and algorithmic logic
├── DATABASE_SCHEMA.md                         # Relational schema and DDL specification
├── DATA_DICTIONARY.md                         # Field-by-field data dictionary
├── README.md                                  # Platform documentation and startup guide
├── SOURCE_MANIFEST.md                         # Code manifest and component inventory
├── VALIDATION_REPORT.md                       # Data validation and reproducibility report
├── requirements.txt                           # Python dependencies
├── run.py                                     # Master CLI runner (seed, test, server, validate)
├── skillpath.db                               # SQLite database with relational constraints
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                          # Settings & environment configuration
│   │   ├── database.py                        # SQLAlchemy engine & SQLite/MySQL pragma
│   │   ├── main.py                            # FastAPI application, middleware, and router mounting
│   │   ├── models.py                          # 11 relational entities + ExceptionRecord ORM models
│   │   ├── schemas.py                         # Pydantic v2 schemas and validation models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py                   # /api/analytics/dashboard metrics & charts
│   │   │   ├── budgets.py                     # /api/budgets endpoints
│   │   │   ├── career.py                      # /api/career-pathways endpoints
│   │   │   ├── completions.py                 # /api/completions endpoints
│   │   │   ├── courses.py                     # /api/courses endpoints
│   │   │   ├── employees.py                   # /api/employees & /api/employees/{id}/skill-gaps
│   │   │   ├── enrollments.py                 # /api/enrollments endpoints
│   │   │   ├── exceptions.py                  # /api/exceptions audit endpoints
│   │   │   ├── recommendations.py             # /api/recommendations endpoints
│   │   │   ├── reports.py                     # /api/reports/export CSV endpoints
│   │   │   └── skills.py                      # /api/skills endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── career_pathway.py              # Career ladder and readiness engine
│   │       ├── exception_tracker.py           # 5 exception scenario handlers
│   │       ├── gap_analysis.py                # MAX(0, Required - Current) calculation engine
│   │       ├── metrics_service.py             # 10 measurable evaluation metrics calculator
│   │       ├── recommendation.py              # 12-step course recommendation engine
│   │       └── tracking_service.py            # Enrollment, completion, and reassessment lifecycle
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── generator.py                       # Synthetic data generator (seed: 20261022)
│   │   └── validator.py                       # Automated relational & reproducibility validator
│   └── tests/
│       ├── __init__.py
│       ├── test_api_endpoints.py              # REST API router test suite
│       └── test_exceptions.py                 # 5 exception scenarios test suite
│
├── data/
│   ├── starter/                               # Generated starter dataset CSV, JSON, and SQL files
│   │   ├── budgets.csv
│   │   ├── completions.csv
│   │   ├── course_skills.csv
│   │   ├── courses.csv
│   │   ├── employee_skills.csv
│   │   ├── employees.csv
│   │   ├── exceptions.csv
│   │   ├── enrollments.csv
│   │   ├── prerequisites.csv
│   │   ├── role_skill_targets.csv
│   │   ├── roles.csv
│   │   ├── skills.csv
│   │   ├── seed.sql                           # MySQL insert script
│   │   └── json/                              # JSON exports
│   └── exports/
│       ├── ground_truth.csv                   # Ground-truth exception labels
│       └── validation_report.json             # Automated validation results JSON
│
└── frontend/
    ├── index.html                             # Single page application host HTML
    ├── package.json                           # React 18, Vite, Tailwind CSS, Recharts
    ├── postcss.config.js                      # PostCSS pipeline
    ├── tailwind.config.js                     # Tailwind enterprise theme configuration
    ├── vite.config.js                         # Vite dev & proxy configuration
    ├── dist/                                  # Production build output bundle
    └── src/
        ├── App.jsx                            # Master React view controller
        ├── index.css                          # Tailwind CSS imports & custom styles
        ├── main.jsx                           # React root mounting
        ├── api/
        │   └── client.js                      # Centralized API fetch client
        ├── components/
        │   ├── Layout.jsx                     # Enterprise sidebar & header navigation
        │   ├── Modal.jsx                      # Reusable modal dialogs & spinners
        │   ├── SeverityBadge.jsx              # Status and severity badges
        │   └── StatCard.jsx                   # Metric KPI display card
        └── pages/
            ├── BudgetsPage.jsx                # Page 7: Budget Management
            ├── CareerPathwaysPage.jsx         # Page 9: Career Pathways
            ├── CoursesPage.jsx                # Page 4: Course Catalogue
            ├── EmployeesPage.jsx              # Page 2: Employees Directory & Profiles
            ├── EnrollmentsPage.jsx            # Page 6: Enrollments & Learning Lifecycle
            ├── ExceptionsPage.jsx             # Page 8: Exception Monitoring
            ├── OverviewPage.jsx               # Page 1: Executive Overview & KPIs
            ├── RecommendationsPage.jsx        # Page 5: Intelligent Recommendations
            ├── ReportsPage.jsx                # Page 10: Reports & CSV Export
            └── SkillGapPage.jsx               # Page 3: Skill Gap Analysis Matrix
```

---

## 2. Component Responsibility Matrix

| Module | Core Responsibilities |
|---|---|
| `backend/app/models.py` | 11 relational entities (`Employee`, `Role`, `Skill`, `RoleSkillTarget`, `EmployeeSkill`, `Course`, `CourseSkill`, `Prerequisite`, `Enrollment`, `Completion`, `Budget`) + `ExceptionRecord`. |
| `backend/app/services/gap_analysis.py` | Implements $\text{MAX}(0, \text{Required} - \text{Current})$, severity categorization (`Met`, `Low`, `Medium`, `High`, `Critical`), department and role rollups. |
| `backend/app/services/recommendation.py` | Implements the 12-step recommendation pipeline, prerequisite checks, budget filtering, seat validation, multi-factor priority scoring, explanations, and rejection reasoning. |
| `backend/app/services/exception_tracker.py` | Captures, audits, and manages the 5 mandated exception scenarios (`PREREQUISITE_VIOLATION`, `BUDGET_EXCEEDED`, `DUPLICATE_COMPLETION`, `UNASSESSED_GAP`, `COURSE_UNAVAILABLE`). |
| `backend/app/services/tracking_service.py` | Enforces the lifecycle state machine: $\text{Attendance} \ne \text{Completion} \ne \text{Skill Improvement}$. Manages enrollments, completions, and reassessments. |
| `backend/app/services/career_pathway.py` | Maps hierarchical department promotion ladders, determines missing competencies for target roles, builds transition roadmaps, and computes career readiness scores. |
| `backend/app/services/metrics_service.py` | Calculates all 10 measurable evaluation metrics using SQL aggregations over relational source data. |
| `backend/generator/generator.py` | Synthetic data generator using fixed seed `20261022`. Generates master and dependent records, exports CSV, JSON, SQL seed, and `ground_truth.csv`. |
| `backend/generator/validator.py` | 11 automated data integrity checks: primary key uniqueness, foreign keys, bounds, enums, dates, budgets, capacities, prerequisites, reassessment gating, and reproducibility. |
| `frontend/src/` | Modern React 18 SaaS dashboard across 10 complete pages with Tailwind CSS, Recharts visualizations, and Lucide icons. |
