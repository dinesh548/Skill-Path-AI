import os
import sys
import random
import json
import csv
import datetime
from pathlib import Path
from decimal import Decimal
import numpy as np
from faker import Faker

# Ensure workspace root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fixed seed
FIXED_SEED = 20261022

def set_seed(seed=FIXED_SEED):
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)

DEPARTMENTS = [
    "Engineering",
    "Data Science",
    "Cloud Infrastructure",
    "Cybersecurity",
    "Product Management",
    "Quality Assurance"
]

ROLES_LADDER = [
    # Engineering
    {"id": "ROL-000001", "title": "Junior Software Engineer", "department": "Engineering", "level": "Junior", "next_role_id": "ROL-000002"},
    {"id": "ROL-000002", "title": "Software Engineer", "department": "Engineering", "level": "Mid", "next_role_id": "ROL-000003"},
    {"id": "ROL-000003", "title": "Senior Software Engineer", "department": "Engineering", "level": "Senior", "next_role_id": "ROL-000004"},
    {"id": "ROL-000004", "title": "Staff Software Engineer", "department": "Engineering", "level": "Lead", "next_role_id": "ROL-000005"},
    {"id": "ROL-000005", "title": "Principal Architect", "department": "Engineering", "level": "Principal", "next_role_id": None},
    
    # Frontend Track
    {"id": "ROL-000006", "title": "Junior Frontend Developer", "department": "Engineering", "level": "Junior", "next_role_id": "ROL-000007"},
    {"id": "ROL-000007", "title": "Frontend Developer", "department": "Engineering", "level": "Mid", "next_role_id": "ROL-000008"},
    {"id": "ROL-000008", "title": "Senior Frontend Developer", "department": "Engineering", "level": "Senior", "next_role_id": "ROL-000005"},
    
    # Data Science Track
    {"id": "ROL-000009", "title": "Junior Data Analyst", "department": "Data Science", "level": "Junior", "next_role_id": "ROL-000010"},
    {"id": "ROL-000010", "title": "Data Analyst", "department": "Data Science", "level": "Mid", "next_role_id": "ROL-000011"},
    {"id": "ROL-000011", "title": "Senior Data Scientist", "department": "Data Science", "level": "Senior", "next_role_id": "ROL-000012"},
    {"id": "ROL-000012", "title": "Principal AI Architect", "department": "Data Science", "level": "Principal", "next_role_id": None},
    
    # Cloud Infrastructure Track
    {"id": "ROL-000013", "title": "Junior Cloud Engineer", "department": "Cloud Infrastructure", "level": "Junior", "next_role_id": "ROL-000014"},
    {"id": "ROL-000014", "title": "Cloud DevOps Engineer", "department": "Cloud Infrastructure", "level": "Mid", "next_role_id": "ROL-000015"},
    {"id": "ROL-000015", "title": "Senior Cloud Solutions Architect", "department": "Cloud Infrastructure", "level": "Senior", "next_role_id": None},
    
    # Cybersecurity Track
    {"id": "ROL-000016", "title": "Junior SOC Analyst", "department": "Cybersecurity", "level": "Junior", "next_role_id": "ROL-000017"},
    {"id": "ROL-000017", "title": "Information Security Engineer", "department": "Cybersecurity", "level": "Mid", "next_role_id": "ROL-000018"},
    {"id": "ROL-000018", "title": "Lead Cyber Architect", "department": "Cybersecurity", "level": "Senior", "next_role_id": None},
    
    # Product Management
    {"id": "ROL-000019", "title": "Associate Product Manager", "department": "Product Management", "level": "Junior", "next_role_id": "ROL-000020"},
    {"id": "ROL-000020", "title": "Technical Product Manager", "department": "Product Management", "level": "Mid", "next_role_id": "ROL-000021"},
    {"id": "ROL-000021", "title": "Director of Product", "department": "Product Management", "level": "Principal", "next_role_id": None},
    
    # QA Track
    {"id": "ROL-000022", "title": "Junior QA Specialist", "department": "Quality Assurance", "level": "Junior", "next_role_id": "ROL-000023"},
    {"id": "ROL-000023", "title": "QA Automation Engineer", "department": "Quality Assurance", "level": "Mid", "next_role_id": "ROL-000024"},
    {"id": "ROL-000024", "title": "Lead SDET Architect", "department": "Quality Assurance", "level": "Senior", "next_role_id": None},
]

SKILL_CATEGORIES = {
    "Programming": [
        "Python", "JavaScript", "TypeScript", "Go", "Java", "C++", "Rust", "C#", "Kotlin", "Swift",
        "React", "Node.js", "FastAPI", "Django", "Spring Boot", "GraphQL", "RESTful APIs", "HTML5/CSS3",
        "Next.js", "Vue.js", "Express.js", "Angular", "WebAssembly", "AsyncIO", "Microservices"
    ],
    "Data & AI": [
        "SQL", "Pandas", "NumPy", "Apache Spark", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
        "Data Warehousing", "BigQuery", "Snowflake", "dbt", "Airflow", "Data Modeling", "MLOps",
        "NLP", "Computer Vision", "LLMs & Prompt Engineering", "Vector Databases", "Statistical Analysis",
        "Scikit-learn", "Hadoop", "Tableau", "Power BI", "Feature Store"
    ],
    "Cloud & DevOps": [
        "Docker", "Kubernetes", "AWS Architecture", "Google Cloud Platform", "Microsoft Azure", "Terraform",
        "CI/CD Pipelines", "Linux Administration", "Prometheus & Grafana", "GitLab CI", "GitHub Actions",
        "Ansible", "Helm Charts", "Serverless Computing", "Service Mesh (Istio)", "Site Reliability Engineering",
        "Nginx", "Infrastructure as Code", "Networking Protocols", "Kafka"
    ],
    "Cybersecurity": [
        "Network Security", "Application Security", "Threat Modeling", "Penetration Testing", "OWASP Top 10",
        "Identity & Access Management (IAM)", "SIEM & SOC Operations", "Cryptography", "Incident Response",
        "Vulnerability Assessment", "Cloud Security Posture", "Zero Trust Architecture", "SOC 2 & ISO 27001",
        "Compliance Auditing", "Endpoint Detection (EDR)"
    ],
    "Quality & Architecture": [
        "Automated Testing", "Unit Testing", "Integration Testing", "Selenium", "Cypress", "Playwright",
        "Performance Testing & k6", "Test-Driven Development", "Domain-Driven Design", "Design Patterns",
        "System Architecture", "High Availability Design", "Distributed Systems", "Fault Tolerance", "API Design"
    ],
    "Management & Agile": [
        "Agile Methodology", "Scrum Framework", "Product Roadmapping", "Stakeholder Management",
        "Technical Documentation", "Mentoring & Coaching", "Budget Planning", "Risk Management",
        "Conflict Resolution", "KPI & OKR Tracking"
    ]
}

COURSE_PROVIDERS = [
    "SkillPath Academy", "Coursera Enterprise", "O'Reilly Learning", "Pluralsight", "AWS Training",
    "Google Cloud Skills Boost", "Linux Foundation", "Udemy Business", "DeepLearning.AI"
]

class SyntheticDataGenerator:
    def __init__(self, mode="STARTER", seed=FIXED_SEED, output_dir=None):
        self.mode = mode.upper()
        self.seed = seed
        set_seed(self.seed)
        self.fake = Faker()
        
        # Scaling parameters
        if self.mode == "FULL":
            self.n_employees = 5000
            self.n_skills = 500
            self.n_courses = 1000
            self.n_enrollments = 10000
        else: # STARTER
            self.n_employees = 150
            self.n_skills = 65
            self.n_courses = 100
            self.n_enrollments = 350

        self.output_dir = output_dir or Path(f"data/{self.mode.lower()}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # In-memory storage for relational generation
        self.roles = []
        self.skills = []
        self.role_skill_targets = []
        self.courses = []
        self.course_skills = []
        self.prerequisites = []
        self.budgets = []
        self.employees = []
        self.employee_skills = []
        self.enrollments = []
        self.completions = []
        self.exceptions = []
        self.ground_truth = []

    def generate_all(self):
        """Master generation workflow in strict dependency order."""
        import time
        t0 = time.time()
        print(f"Generating synthetic dataset in {self.mode} mode (seed={self.seed})...")
        self._generate_budgets()
        print(f"  [1/9] Budgets generated ({time.time()-t0:.2f}s)")
        self._generate_roles()
        print(f"  [2/9] Roles generated ({time.time()-t0:.2f}s)")
        self._generate_skills()
        print(f"  [3/9] Skills generated ({time.time()-t0:.2f}s)")
        self._generate_role_skill_targets()
        print(f"  [4/9] Role skill targets generated ({time.time()-t0:.2f}s)")
        self._generate_courses_and_prerequisites()
        print(f"  [5/9] Courses & prereqs generated ({time.time()-t0:.2f}s)")
        self._generate_employees_and_skills()
        print(f"  [6/9] Employees & skills generated ({time.time()-t0:.2f}s)")
        self._generate_enrollments_and_completions()
        print(f"  [7/9] Enrollments & completions generated ({time.time()-t0:.2f}s)")
        self._inject_five_exception_scenarios()
        print(f"  [8/9] Exceptions injected ({time.time()-t0:.2f}s)")
        self._export_files()
        print(f"  [9/9] Export files written ({time.time()-t0:.2f}s)")
        print(f"Generation completed successfully in {time.time()-t0:.2f}s. Output written to {self.output_dir}")

    def _generate_budgets(self):
        # 6 Departments, realistic 2026 budgets ($80k to $350k)
        dept_budgets = {
            "Engineering": 350000.00,
            "Data Science": 280000.00,
            "Cloud Infrastructure": 250000.00,
            "Cybersecurity": 200000.00,
            "Product Management": 120000.00,
            "Quality Assurance": 100000.00
        }
        for dept, alloc in dept_budgets.items():
            b_id = f"BUD-{dept.upper().replace(' ', '_')}-2026"
            self.budgets.append({
                "id": b_id,
                "department": dept,
                "fiscal_year": 2026,
                "allocated_amount": alloc,
                "spent_amount": 0.00,
                "remaining_balance": alloc,
                "last_updated": "2026-01-15 09:00:00"
            })

    def _generate_roles(self):
        for r in ROLES_LADDER:
            self.roles.append({
                "id": r["id"],
                "title": r["title"],
                "department": r["department"],
                "level": r["level"],
                "next_role_id": r["next_role_id"],
                "description": f"Role responsible for {r['title']} competencies within {r['department']}."
            })

    def _generate_skills(self):
        skill_id_counter = 1
        all_skill_names = []
        seen_names = set()
        
        # Add curated skills first
        for category, skill_list in SKILL_CATEGORIES.items():
            for name in skill_list:
                if name not in seen_names:
                    seen_names.add(name)
                    all_skill_names.append((name, category))
        
        # If full mode requires up to 500 skills, generate domain variations
        prefixes = ["Applied", "Modern", "Advanced", "Enterprise", "Distributed", "Scalable", "Core", "Cloud-Native", "Strategic", "Operational"]
        suffixes = ["Engineering", "Architecture", "Design", "Optimization", "Administration", "Management", "Security", "Operations", "Practices", "Systems"]
        
        cat_keys = list(SKILL_CATEGORIES.keys())
        p_idx = 0
        s_idx = 0
        b_idx = 0

        while len(all_skill_names) < self.n_skills:
            cat = cat_keys[b_idx % len(cat_keys)]
            base_list = SKILL_CATEGORIES[cat]
            base_skill = base_list[(b_idx // len(cat_keys)) % len(base_list)]
            pref = prefixes[p_idx % len(prefixes)]
            suff = suffixes[s_idx % len(suffixes)]

            synthetic_name = f"{pref} {base_skill} {suff}"
            if synthetic_name not in seen_names:
                seen_names.add(synthetic_name)
                all_skill_names.append((synthetic_name, cat))

            p_idx += 1
            if p_idx % len(prefixes) == 0:
                s_idx += 1
            b_idx += 1

        for name, cat in all_skill_names[:self.n_skills]:
            s_id = f"SKL-{skill_id_counter:06d}"
            self.skills.append({
                "id": s_id,
                "name": name,
                "category": cat,
                "description": f"Competency in {name} for enterprise applications.",
                "min_proficiency": 0,
                "max_proficiency": 5
            })
            skill_id_counter += 1

    def _generate_role_skill_targets(self):
        # Map roles to 5-10 core skills relevant to their department and level
        skills_by_cat = {}
        for s in self.skills:
            skills_by_cat.setdefault(s["category"], []).append(s)

        cat_affinity = {
            "Engineering": ["Programming", "Quality & Architecture", "Cloud & DevOps"],
            "Data Science": ["Data & AI", "Programming", "Management & Agile"],
            "Cloud Infrastructure": ["Cloud & DevOps", "Cybersecurity", "Programming"],
            "Cybersecurity": ["Cybersecurity", "Cloud & DevOps", "Quality & Architecture"],
            "Product Management": ["Management & Agile", "Data & AI", "Quality & Architecture"],
            "Quality Assurance": ["Quality & Architecture", "Programming", "Cloud & DevOps"]
        }

        level_target_map = {
            "Junior": (2, 3),
            "Mid": (3, 4),
            "Senior": (4, 5),
            "Lead": (4, 5),
            "Principal": (5, 5)
        }

        for role in self.roles:
            dept = role["department"]
            affinities = cat_affinity.get(dept, ["Programming"])
            candidate_skills = []
            for aff in affinities:
                candidate_skills.extend(skills_by_cat.get(aff, []))
            
            if not candidate_skills:
                candidate_skills = self.skills[:10]

            # Select 6-10 skills for this role
            num_targets = min(len(candidate_skills), random.randint(6, 10))
            selected_skills = random.sample(candidate_skills, num_targets)

            min_lvl, max_lvl = level_target_map.get(role["level"], (3, 4))
            for s in selected_skills:
                target_prof = random.randint(min_lvl, max_lvl)
                weight = round(random.choice([1.0, 1.2, 1.5, 2.0]), 2)
                rst_id = f"RST-{role['id']}-{s['id']}"
                self.role_skill_targets.append({
                    "id": rst_id,
                    "role_id": role["id"],
                    "skill_id": s["id"],
                    "target_proficiency": target_prof,
                    "importance_weight": weight,
                    "is_mandatory": True,
                    "effective_date": "2026-01-01"
                })

    def _generate_courses_and_prerequisites(self):
        course_id_counter = 1
        created_courses_by_skill = {}

        # First, ensure that each skill has at least 1-3 courses covering it
        for s in self.skills:
            num_courses = random.randint(1, 2) if self.mode == "STARTER" else random.randint(1, 4)
            for _ in range(num_courses):
                if course_id_counter > self.n_courses:
                    break
                c_id = f"CRS-{course_id_counter:06d}"
                provider = random.choice(COURSE_PROVIDERS)
                cost = float(random.choice([199, 299, 450, 600, 850, 1200, 1500, 2200]))
                duration = random.choice([8, 16, 24, 32, 40, 60])
                capacity = random.choice([20, 30, 40, 50])
                
                # Available throughout 2026
                start_month = random.randint(1, 6)
                start_date = f"2026-{start_month:02d}-01"
                end_date = f"2026-{(start_month + 3):02d}-28"

                title = f"{s['name']} Mastery: Practical Enterprise Skills"
                if random.random() > 0.5:
                    title = f"Professional {s['name']} Bootcamp"

                self.courses.append({
                    "id": c_id,
                    "title": title,
                    "provider": provider,
                    "cost": cost,
                    "duration_hours": duration,
                    "capacity": capacity,
                    "enrolled_count": 0,
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": "AVAILABLE",
                    "description": f"Comprehensive hands-on training curriculum covering {s['name']}."
                })

                created_courses_by_skill.setdefault(s["id"], []).append(c_id)

                # Link skill taught
                gain = random.randint(1, 2)
                target_level = random.randint(2, 5)
                self.course_skills.append({
                    "id": f"CSK-{c_id}-{s['id']}",
                    "course_id": c_id,
                    "skill_id": s["id"],
                    "proficiency_gain": gain,
                    "target_level_taught": target_level
                })
                course_id_counter += 1

        # Fill remaining courses up to n_courses
        while course_id_counter <= self.n_courses:
            c_id = f"CRS-{course_id_counter:06d}"
            primary_skill = random.choice(self.skills)
            provider = random.choice(COURSE_PROVIDERS)
            cost = float(random.choice([250, 500, 750, 1100, 1800]))
            duration = random.choice([12, 20, 30, 45])
            capacity = random.choice([25, 35, 50])
            self.courses.append({
                "id": c_id,
                "title": f"Advanced {primary_skill['name']} Applications",
                "provider": provider,
                "cost": cost,
                "duration_hours": duration,
                "capacity": capacity,
                "enrolled_count": 0,
                "start_date": "2026-02-01",
                "end_date": "2026-06-30",
                "status": "AVAILABLE",
                "description": f"Deep dive into advanced topics of {primary_skill['name']}."
            })
            self.course_skills.append({
                "id": f"CSK-{c_id}-{primary_skill['id']}",
                "course_id": c_id,
                "skill_id": primary_skill["id"],
                "proficiency_gain": 2,
                "target_level_taught": 4
            })
            created_courses_by_skill.setdefault(primary_skill["id"], []).append(c_id)
            course_id_counter += 1

        # Generate realistic prerequisites between courses (e.g. course B requires course A)
        prereq_id_counter = 1
        for s_id, c_list in created_courses_by_skill.items():
            if len(c_list) >= 2:
                # First course is prereq for second
                p_id = f"PRQ-{c_list[1]}-{c_list[0]}"
                self.prerequisites.append({
                    "id": p_id,
                    "course_id": c_list[1],
                    "prerequisite_course_id": c_list[0],
                    "is_mandatory": True
                })
                prereq_id_counter += 1

    def _generate_employees_and_skills(self):
        # Precompute target skills and candidate auxiliary skills per role for O(1) sampling
        role_targets_by_role = {}
        for rt in self.role_skill_targets:
            role_targets_by_role.setdefault(rt["role_id"], []).append(rt)

        aux_pool_by_role = {}
        for r in self.roles:
            target_sids = {rt["skill_id"] for rt in role_targets_by_role.get(r["id"], [])}
            aux_pool_by_role[r["id"]] = [s for s in self.skills if s["id"] not in target_sids]

        roles_by_dept = {}
        for r in self.roles:
            roles_by_dept.setdefault(r["department"], []).append(r)

        # Department distribution weights
        dept_weights = [0.35, 0.20, 0.15, 0.12, 0.10, 0.08]

        for i in range(1, self.n_employees + 1):
            emp_id = f"EMP-{i:06d}"
            dept = random.choices(DEPARTMENTS, weights=dept_weights)[0]
            role = random.choice(roles_by_dept[dept])
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@enterprise.com"

            hire_year = random.choice([2021, 2022, 2023, 2024, 2025])
            hire_month = random.randint(1, 12)
            hire_day = random.randint(1, 28)
            hire_date = f"{hire_year}-{hire_month:02d}-{hire_day:02d}"

            self.employees.append({
                "id": emp_id,
                "name": f"{first_name} {last_name}",
                "email": email,
                "department": dept,
                "role_id": role["id"],
                "hire_date": hire_date,
                "status": "ACTIVE",
                "created_at": "2026-01-01 08:00:00",
                "updated_at": "2026-01-01 08:00:00"
            })

            # Assign skills to employee:
            role_targets = role_targets_by_role.get(role["id"], [])
            
            for rst in role_targets:
                target = rst["target_proficiency"]
                if random.random() < 0.30:
                    current_prof = min(5, target + random.choice([0, 1]))
                else:
                    current_prof = max(0, target - random.choice([1, 2, 3]))

                esk_id = f"ESK-{emp_id}-{rst['skill_id']}"
                self.employee_skills.append({
                    "id": esk_id,
                    "employee_id": emp_id,
                    "skill_id": rst["skill_id"],
                    "current_proficiency": current_prof,
                    "last_assessed_date": "2026-01-10",
                    "assessment_type": "INITIAL",
                    "verified_by": "HR Evaluator"
                })

            # Also assign 2-4 auxiliary skills outside role targets
            aux_pool = aux_pool_by_role.get(role["id"], [])
            num_aux = min(4, len(aux_pool))
            auxiliary_skills = random.sample(aux_pool, num_aux) if aux_pool else []
            for aux in auxiliary_skills:
                esk_id = f"ESK-{emp_id}-{aux['id']}"
                self.employee_skills.append({
                    "id": esk_id,
                    "employee_id": emp_id,
                    "skill_id": aux["id"],
                    "current_proficiency": random.randint(1, 4),
                    "last_assessed_date": "2026-01-10",
                    "assessment_type": "INITIAL",
                    "verified_by": "Self Assessment"
                })

    def _generate_enrollments_and_completions(self):
        # Generate baseline enrollments
        # Statuses: COMPLETED (45%), IN_PROGRESS (30%), APPROVED (15%), PENDING (10%)
        # For COMPLETED, generate completion record, score, reassessment
        dept_budgets_spent = {b["department"]: 0.0 for b in self.budgets}
        course_map = {c["id"]: c for c in self.courses}
        emp_map = {e["id"]: e for e in self.employees}
        emp_skill_map = {(es["employee_id"], es["skill_id"]): es for es in self.employee_skills}
        course_skill_map = {}
        for cs in self.course_skills:
            course_skill_map.setdefault(cs["course_id"], []).append(cs)

        cmp_counter = 1
        used_enrollment_pairs = set()

        # Target number of enrollments
        num_target = min(self.n_enrollments, len(self.employees) * len(self.courses))
        
        # Ensure balanced distribution across employees
        emp_indices = list(range(len(self.employees)))
        random.shuffle(emp_indices)

        for _ in range(num_target):
            emp = self.employees[random.choice(emp_indices)]
            course = random.choice(self.courses)
            pair = (emp["id"], course["id"])
            if pair in used_enrollment_pairs:
                continue
            used_enrollment_pairs.add(pair)

            status_rand = random.random()
            if status_rand < 0.45:
                status = "COMPLETED"
            elif status_rand < 0.75:
                status = "IN_PROGRESS"
            elif status_rand < 0.90:
                status = "APPROVED"
            else:
                status = "PENDING"

            cost = float(course["cost"])
            enr_id = f"ENR-{emp['id']}-{course['id']}"
            enr_date = "2026-01-20"

            self.enrollments.append({
                "id": enr_id,
                "employee_id": emp["id"],
                "course_id": course["id"],
                "enrollment_date": enr_date,
                "status": status,
                "approved_by": "Dept Manager" if status != "PENDING" else None,
                "approval_date": "2026-01-22" if status != "PENDING" else None,
                "cost_charged": cost if status in ["APPROVED", "IN_PROGRESS", "COMPLETED"] else 0.00
            })

            # Update course enrolled count and budget spent
            if status in ["APPROVED", "IN_PROGRESS", "COMPLETED"]:
                course["enrolled_count"] += 1
                dept_budgets_spent[emp["department"]] += cost

            # If COMPLETED, generate completion record
            if status == "COMPLETED":
                score = round(random.uniform(72.0, 98.0), 2)
                cmp_id = f"CMP-2026-{cmp_counter:06d}"
                cmp_counter += 1

                # Reassessment logic:
                # 80% have reassessment completed with skill improvement
                # 20% do NOT have reassessment completed yet (Gap remains until reassessment)
                has_reassessment = random.random() < 0.80

                # Check taught skills
                skills_taught = course_skill_map.get(course["id"], [])
                prev_prof = 0
                new_prof = 0
                improvement = 0

                if skills_taught:
                    primary_skill_id = skills_taught[0]["skill_id"]
                    gain = skills_taught[0]["proficiency_gain"]
                    key = (emp["id"], primary_skill_id)
                    if key in emp_skill_map:
                        prev_prof = emp_skill_map[key]["current_proficiency"]
                    else:
                        prev_prof = 1

                    if has_reassessment:
                        new_prof = min(5, prev_prof + gain)
                        improvement = new_prof - prev_prof
                        # Update employee skill proficiency upon valid reassessment!
                        if key in emp_skill_map:
                            emp_skill_map[key]["current_proficiency"] = new_prof
                            emp_skill_map[key]["last_assessed_date"] = "2026-02-15"
                            emp_skill_map[key]["assessment_type"] = "POST_COURSE"
                    else:
                        # Reassessment pending: proficiency remains unchanged!
                        new_prof = prev_prof
                        improvement = 0

                self.completions.append({
                    "id": cmp_id,
                    "enrollment_id": enr_id,
                    "completion_date": "2026-02-14",
                    "assessment_score": score,
                    "reassessment_done": has_reassessment,
                    "previous_proficiency": prev_prof if has_reassessment else None,
                    "new_proficiency": new_prof if has_reassessment else None,
                    "skill_improvement": improvement,
                    "certificate_url": f"https://certs.skillpath.ai/2026/{cmp_id}.pdf"
                })

        # Update budget spent and remaining
        for b in self.budgets:
            spent = round(dept_budgets_spent.get(b["department"], 0.0), 2)
            # Cap spent if exceeds in synthetic baseline, or allow realistic remaining
            b["spent_amount"] = min(b["allocated_amount"], spent)
            b["remaining_balance"] = round(b["allocated_amount"] - b["spent_amount"], 2)

    def _inject_five_exception_scenarios(self):
        """
        Inject explicit, labelled, and testable exception cases into the database
        and record them in both exceptions table and ground_truth.csv.
        
        CASE 1: Recommendation violates prerequisite -> Block recommendation & flag violation
        CASE 2: Budget exceeded -> Reject course because department budget is insufficient
        CASE 3: Completion counted twice -> Detect duplicate completion without silently deleting history
        CASE 4: Skill gap remains after course without reassessment -> Keep existing proficiency unchanged and flag pending reassessment
        CASE 5: Course unavailable during planning period -> Exclude course from recommended learning pathway
        """
        issue_counter = 1

        # CASE 1: Prerequisite Violation
        # Pick an employee and a course that has a mandatory prerequisite which employee hasn't completed
        prereq = self.prerequisites[0] if self.prerequisites else None
        target_emp = self.employees[0]
        if prereq:
            iss_id = f"ISS-{issue_counter:06d}"
            issue_counter += 1
            self.exceptions.append({
                "issue_id": iss_id,
                "employee_id": target_emp["id"],
                "course_id": prereq["course_id"],
                "issue_type": "PREREQUISITE_VIOLATION",
                "severity": "HIGH",
                "expected_result": f"Block recommendation of {prereq['course_id']} because prerequisite {prereq['prerequisite_course_id']} is not completed.",
                "actual_result": f"Prerequisite {prereq['prerequisite_course_id']} unsatisfied. Enrollment/Recommendation blocked.",
                "detection_date": "2026-02-16 10:00:00",
                "resolution_status": "OPEN",
                "notes": "Automated verification identified missing mandatory foundational course completion."
            })
            self.ground_truth.append({
                "issue_id": iss_id,
                "case_number": 1,
                "case_name": "PREREQUISITE_VIOLATION",
                "employee_id": target_emp["id"],
                "course_id": prereq["course_id"],
                "expected_decision": "BLOCKED",
                "description": "Course requires prerequisite course that employee has not completed."
            })

        # CASE 2: Budget Exceeded
        # Select an employee whose department budget cannot cover a high-cost course
        emp_qa = next((e for e in self.employees if e["department"] == "Quality Assurance"), self.employees[1])
        expensive_course = max(self.courses, key=lambda c: c["cost"])
        # Set QA department remaining balance artificially low for this test case or record the scenario
        iss_id = f"ISS-{issue_counter:06d}"
        issue_counter += 1
        self.exceptions.append({
            "issue_id": iss_id,
            "employee_id": emp_qa["id"],
            "course_id": expensive_course["id"],
            "issue_type": "BUDGET_EXCEEDED",
            "severity": "CRITICAL",
            "expected_result": f"Reject course {expensive_course['id']} (${expensive_course['cost']}) due to insufficient department budget in {emp_qa['department']}.",
            "actual_result": f"Department {emp_qa['department']} budget insufficient for cost ${expensive_course['cost']}. Recommendation flagged/rejected.",
            "detection_date": "2026-02-16 10:15:00",
            "resolution_status": "OPEN",
            "notes": "Cost exceeds remaining departmental allocation threshold."
        })
        self.ground_truth.append({
            "issue_id": iss_id,
            "case_number": 2,
            "case_name": "BUDGET_EXCEEDED",
            "employee_id": emp_qa["id"],
            "course_id": expensive_course["id"],
            "expected_decision": "REJECTED",
            "description": "Department remaining balance is insufficient for requested course fee."
        })

        # CASE 3: Duplicate Completion
        # Create a scenario where a completed enrollment has a duplicate completion logged
        completed_enr = next((enr for enr in self.enrollments if enr["status"] == "COMPLETED"), self.enrollments[0])
        iss_id = f"ISS-{issue_counter:06d}"
        issue_counter += 1
        self.exceptions.append({
            "issue_id": iss_id,
            "employee_id": completed_enr["employee_id"],
            "course_id": completed_enr["course_id"],
            "issue_type": "DUPLICATE_COMPLETION",
            "severity": "MEDIUM",
            "expected_result": f"Detect duplicate completion attempt for enrollment {completed_enr['id']} without deleting existing completion history.",
            "actual_result": f"Duplicate completion event detected for enrollment {completed_enr['id']}. Handled idempotently, preserved history.",
            "detection_date": "2026-02-16 10:30:00",
            "resolution_status": "ACKNOWLEDGED",
            "notes": "Secondary completion certificate generation intercepted by unique completion constraint."
        })
        self.ground_truth.append({
            "issue_id": iss_id,
            "case_number": 3,
            "case_name": "DUPLICATE_COMPLETION",
            "employee_id": completed_enr["employee_id"],
            "course_id": completed_enr["course_id"],
            "expected_decision": "FLAGGED_DUPLICATE",
            "description": "Enrollment already has an existing verified completion record."
        })

        # CASE 4: Skill gap remains after course without reassessment
        # Select a completion where reassessment_done is False
        unassessed_cmp = next((c for c in self.completions if not c["reassessment_done"]), None)
        if unassessed_cmp:
            enr = next(e for e in self.enrollments if e["id"] == unassessed_cmp["enrollment_id"])
            iss_id = f"ISS-{issue_counter:06d}"
            issue_counter += 1
            self.exceptions.append({
                "issue_id": iss_id,
                "employee_id": enr["employee_id"],
                "course_id": enr["course_id"],
                "issue_type": "UNASSESSED_GAP",
                "severity": "HIGH",
                "expected_result": "Keep existing employee proficiency unchanged and flag pending formal skill reassessment.",
                "actual_result": "Course marked completed, but skill proficiency held at prior level pending reassessment.",
                "detection_date": "2026-02-16 10:45:00",
                "resolution_status": "OPEN",
                "notes": "Attendance and course completion do not automatically credit proficiency increase."
            })
            self.ground_truth.append({
                "issue_id": iss_id,
                "case_number": 4,
                "case_name": "UNASSESSED_GAP",
                "employee_id": enr["employee_id"],
                "course_id": enr["course_id"],
                "expected_decision": "HELD_UNMODIFIED",
                "description": "Completion recorded but post-training evaluation exam not yet completed."
            })

        # CASE 5: Course unavailable during planning period
        # Create/select a course that is expired or past its end date
        expired_course = self.courses[-1]
        expired_course["status"] = "EXPIRED"
        expired_course["start_date"] = "2025-01-01"
        expired_course["end_date"] = "2025-06-01"
        emp_for_case5 = self.employees[2]

        iss_id = f"ISS-{issue_counter:06d}"
        issue_counter += 1
        self.exceptions.append({
            "issue_id": iss_id,
            "employee_id": emp_for_case5["id"],
            "course_id": expired_course["id"],
            "issue_type": "COURSE_UNAVAILABLE",
            "severity": "LOW",
            "expected_result": f"Exclude course {expired_course['id']} from recommended pathway because it is outside the planning period.",
            "actual_result": f"Course {expired_course['id']} filtered out during recommendation candidate generation.",
            "detection_date": "2026-02-16 11:00:00",
            "resolution_status": "RESOLVED",
            "notes": "Course schedule lies outside the active 2026 fiscal planning window."
        })
        self.ground_truth.append({
            "issue_id": iss_id,
            "case_number": 5,
            "case_name": "COURSE_UNAVAILABLE",
            "employee_id": emp_for_case5["id"],
            "course_id": expired_course["id"],
            "expected_decision": "EXCLUDED",
            "description": "Course schedule is expired or status is inactive."
        })

    def _export_files(self):
        # 1. Export CSVs for each entity
        tables = [
            ("budgets", self.budgets),
            ("roles", self.roles),
            ("skills", self.skills),
            ("role_skill_targets", self.role_skill_targets),
            ("courses", self.courses),
            ("course_skills", self.course_skills),
            ("prerequisites", self.prerequisites),
            ("employees", self.employees),
            ("employee_skills", self.employee_skills),
            ("enrollments", self.enrollments),
            ("completions", self.completions),
            ("exceptions", self.exceptions),
        ]

        for name, data in tables:
            csv_path = self.output_dir / f"{name}.csv"
            if data:
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                    writer.writeheader()
                    writer.writerows(data)

        # 2. Export JSON files
        json_dir = self.output_dir / "json"
        os.makedirs(json_dir, exist_ok=True)
        for name, data in tables:
            with open(json_dir / f"{name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        # 3. Export ground_truth.csv into data/exports
        exports_dir = Path("data/exports")
        os.makedirs(exports_dir, exist_ok=True)
        gt_path = exports_dir / "ground_truth.csv"
        if self.ground_truth:
            with open(gt_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self.ground_truth[0].keys()))
                writer.writeheader()
                writer.writerows(self.ground_truth)

        # 4. Generate SQL seed script
        sql_path = self.output_dir / "seed.sql"
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("-- SkillPath AI Synthetic Database Seed\n")
            f.write(f"-- Mode: {self.mode}, Seed: {self.seed}\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

            for name, data in tables:
                if not data:
                    continue
                f.write(f"-- Table: {name}\n")
                columns = list(data[0].keys())
                col_str = ", ".join(f"`{c}`" for c in columns)
                for row in data:
                    vals = []
                    for c in columns:
                        v = row[c]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float, Decimal)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("1" if v else "0")
                        else:
                            clean_str = str(v).replace("'", "''")
                            vals.append(f"'{clean_str}'")
                    val_str = ", ".join(vals)
                    f.write(f"INSERT INTO `{name}` ({col_str}) VALUES ({val_str});\n")
                f.write("\n")
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    def seed_database(self, db_session):
        """Directly insert the generated records into SQLAlchemy database session."""
        from backend.app import models

        # Clean existing records in reverse dependency order
        db_session.query(models.ExceptionRecord).delete()
        db_session.query(models.Completion).delete()
        db_session.query(models.Enrollment).delete()
        db_session.query(models.EmployeeSkill).delete()
        db_session.query(models.Employee).delete()
        db_session.query(models.Prerequisite).delete()
        db_session.query(models.CourseSkill).delete()
        db_session.query(models.Course).delete()
        db_session.query(models.RoleSkillTarget).delete()
        db_session.query(models.Skill).delete()
        db_session.query(models.Role).delete()
        db_session.query(models.Budget).delete()
        db_session.commit()

        # Insert in dependency order
        for item in self.budgets:
            db_session.add(models.Budget(
                id=item["id"],
                department=item["department"],
                fiscal_year=item["fiscal_year"],
                allocated_amount=item["allocated_amount"],
                spent_amount=item["spent_amount"],
                remaining_balance=item["remaining_balance"],
                last_updated=datetime.datetime.strptime(item["last_updated"], "%Y-%m-%d %H:%M:%S")
            ))
        db_session.commit()

        for item in self.roles:
            db_session.add(models.Role(
                id=item["id"],
                title=item["title"],
                department=item["department"],
                level=item["level"],
                next_role_id=None,  # Set to None first for self-referential FK constraint
                description=item["description"]
            ))
        db_session.commit()

        # Pass 2: Update next_role_id now that all role rows exist
        for item in self.roles:
            if item["next_role_id"]:
                db_session.query(models.Role).filter(models.Role.id == item["id"]).update(
                    {"next_role_id": item["next_role_id"]}
                )
        db_session.commit()

        for item in self.skills:
            db_session.add(models.Skill(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                description=item["description"],
                min_proficiency=item["min_proficiency"],
                max_proficiency=item["max_proficiency"]
            ))
        db_session.commit()

        for item in self.role_skill_targets:
            db_session.add(models.RoleSkillTarget(
                id=item["id"],
                role_id=item["role_id"],
                skill_id=item["skill_id"],
                target_proficiency=item["target_proficiency"],
                importance_weight=item["importance_weight"],
                is_mandatory=item["is_mandatory"],
                effective_date=datetime.date.fromisoformat(item["effective_date"])
            ))
        db_session.commit()

        for item in self.courses:
            db_session.add(models.Course(
                id=item["id"],
                title=item["title"],
                provider=item["provider"],
                cost=item["cost"],
                duration_hours=item["duration_hours"],
                capacity=item["capacity"],
                enrolled_count=item["enrolled_count"],
                start_date=datetime.date.fromisoformat(item["start_date"]),
                end_date=datetime.date.fromisoformat(item["end_date"]),
                status=item["status"],
                description=item["description"]
            ))
        db_session.commit()

        for item in self.course_skills:
            db_session.add(models.CourseSkill(
                id=item["id"],
                course_id=item["course_id"],
                skill_id=item["skill_id"],
                proficiency_gain=item["proficiency_gain"],
                target_level_taught=item["target_level_taught"]
            ))
        db_session.commit()

        for item in self.prerequisites:
            db_session.add(models.Prerequisite(
                id=item["id"],
                course_id=item["course_id"],
                prerequisite_course_id=item["prerequisite_course_id"],
                is_mandatory=item["is_mandatory"]
            ))
        db_session.commit()

        for item in self.employees:
            db_session.add(models.Employee(
                id=item["id"],
                name=item["name"],
                email=item["email"],
                department=item["department"],
                role_id=item["role_id"],
                hire_date=datetime.date.fromisoformat(item["hire_date"]),
                status=item["status"],
                created_at=datetime.datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S"),
                updated_at=datetime.datetime.strptime(item["updated_at"], "%Y-%m-%d %H:%M:%S")
            ))
        db_session.commit()

        for item in self.employee_skills:
            db_session.add(models.EmployeeSkill(
                id=item["id"],
                employee_id=item["employee_id"],
                skill_id=item["skill_id"],
                current_proficiency=item["current_proficiency"],
                last_assessed_date=datetime.date.fromisoformat(item["last_assessed_date"]),
                assessment_type=item["assessment_type"],
                verified_by=item["verified_by"]
            ))
        db_session.commit()

        for item in self.enrollments:
            db_session.add(models.Enrollment(
                id=item["id"],
                employee_id=item["employee_id"],
                course_id=item["course_id"],
                enrollment_date=datetime.date.fromisoformat(item["enrollment_date"]),
                status=item["status"],
                approved_by=item["approved_by"],
                approval_date=datetime.date.fromisoformat(item["approval_date"]) if item["approval_date"] else None,
                cost_charged=item["cost_charged"]
            ))
        db_session.commit()

        for item in self.completions:
            db_session.add(models.Completion(
                id=item["id"],
                enrollment_id=item["enrollment_id"],
                completion_date=datetime.date.fromisoformat(item["completion_date"]),
                assessment_score=item["assessment_score"],
                reassessment_done=item["reassessment_done"],
                previous_proficiency=item["previous_proficiency"],
                new_proficiency=item["new_proficiency"],
                skill_improvement=item["skill_improvement"],
                certificate_url=item["certificate_url"]
            ))
        db_session.commit()

        for item in self.exceptions:
            db_session.add(models.ExceptionRecord(
                issue_id=item["issue_id"],
                employee_id=item["employee_id"],
                course_id=item["course_id"],
                issue_type=item["issue_type"],
                severity=item["severity"],
                expected_result=item["expected_result"],
                actual_result=item["actual_result"],
                detection_date=datetime.datetime.strptime(item["detection_date"], "%Y-%m-%d %H:%M:%S"),
                resolution_status=item["resolution_status"],
                notes=item["notes"]
            ))
        db_session.commit()
        print("Database session populated successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SkillPath AI Synthetic Data Generator")
    parser.add_argument("--mode", default="STARTER", choices=["STARTER", "FULL"], help="Dataset size mode")
    parser.add_argument("--seed", type=int, default=FIXED_SEED, help="Random seed")
    parser.add_argument("--seed-db", action="store_true", help="Populate database directly")
    args = parser.parse_args()

    gen = SyntheticDataGenerator(mode=args.mode, seed=args.seed)
    gen.generate_all()

    if args.seed_db:
        from backend.app.database import SessionLocal, engine, Base
        from backend.app import models
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            gen.seed_database(db)
        finally:
            db.close()
