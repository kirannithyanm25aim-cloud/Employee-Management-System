"""
In-Memory Employee Service for Employee Hub.
Provides thread-safe-like in-memory CRUD operations, analytics,
search, filtering, and reporting without any database.
"""
import copy
import csv
import io
from datetime import datetime

# Curated gradients for avatar initials to give a sleek SaaS feel
AVATAR_GRADIENTS = [
    "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",  # Indigo -> Purple
    "linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)",  # Blue -> Cyan
    "linear-gradient(135deg, #10b981 0%, #14b8a6 100%)",  # Emerald -> Teal
    "linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)",  # Amber -> Red
    "linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)",  # Pink -> Violet
    "linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)",  # Violet -> Blue
    "linear-gradient(135deg, #14b8a6 0%, #3b82f6 100%)",  # Teal -> Blue
    "linear-gradient(135deg, #f97316 0%, #f43f5e 100%)",  # Orange -> Rose
]

DEPARTMENT_META = {
    "IT": {
        "icon": "fa-laptop-code",
        "color": "#38bdf8",
        "bg_color": "rgba(56, 189, 248, 0.12)",
        "description": "Software architecture, cloud infrastructure, and security engineering.",
    },
    "HR": {
        "icon": "fa-users-gear",
        "color": "#f472b6",
        "bg_color": "rgba(244, 114, 182, 0.12)",
        "description": "Talent acquisition, organizational culture, and employee welfare.",
    },
    "Finance": {
        "icon": "fa-chart-pie",
        "color": "#34d399",
        "bg_color": "rgba(52, 211, 153, 0.12)",
        "description": "Financial planning, accounting, investment strategy, and payroll.",
    },
    "Marketing": {
        "icon": "fa-bullhorn",
        "color": "#fbbf24",
        "bg_color": "rgba(251, 191, 36, 0.12)",
        "description": "Brand positioning, growth marketing, digital campaigns, and PR.",
    },
    "Sales": {
        "icon": "fa-handshake",
        "color": "#818cf8",
        "bg_color": "rgba(129, 140, 248, 0.12)",
        "description": "Enterprise solutions, account executive management, and partnerships.",
    },
    "Operations": {
        "icon": "fa-gears",
        "color": "#a78bfa",
        "bg_color": "rgba(167, 139, 250, 0.12)",
        "description": "Business efficiency, process optimization, logistics, and compliance.",
    },
}

def get_initials(name):
    """Generate 2-letter uppercase initials from full name."""
    parts = [p.strip() for p in (name or "").strip().split() if p.strip()]
    if not parts:
        return "EH"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def get_avatar_gradient(name):
    """Deterministically pick a vibrant gradient based on name hash."""
    if not name:
        return AVATAR_GRADIENTS[0]
    hash_code = sum(ord(c) for c in name)
    return AVATAR_GRADIENTS[hash_code % len(AVATAR_GRADIENTS)]

# Initial realistic sample dataset (14 employees across 6 departments)
INITIAL_SAMPLE_EMPLOYEES = [
    {
        "id": "EMP-1001",
        "full_name": "Alexander Wright",
        "email": "alexander.wright@employeehub.io",
        "phone": "+1 (555) 234-8901",
        "gender": "Male",
        "dob": "1989-05-14",
        "department": "IT",
        "designation": "Principal Cloud Architect",
        "salary": 142000,
        "joining_date": "2021-03-15",
        "status": "Active",
        "address": "742 Innovation Way, Suite 400, San Francisco, CA",
    },
    {
        "id": "EMP-1002",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@employeehub.io",
        "phone": "+1 (555) 876-5432",
        "gender": "Female",
        "dob": "1993-08-22",
        "department": "HR",
        "designation": "Head of People & Culture",
        "salary": 108000,
        "joining_date": "2021-08-01",
        "status": "Active",
        "address": "120 Park Avenue, Apt 14B, New York, NY",
    },
    {
        "id": "EMP-1003",
        "full_name": "Marcus Vance",
        "email": "marcus.vance@employeehub.io",
        "phone": "+1 (555) 432-1098",
        "gender": "Male",
        "dob": "1986-11-30",
        "department": "Finance",
        "designation": "Director of Strategic Finance",
        "salary": 138000,
        "joining_date": "2020-11-10",
        "status": "Active",
        "address": "55 Wall Street, Floor 18, New York, NY",
    },
    {
        "id": "EMP-1004",
        "full_name": "Elena Rostova",
        "email": "elena.rostova@employeehub.io",
        "phone": "+1 (555) 654-7890",
        "gender": "Female",
        "dob": "1994-02-18",
        "department": "Marketing",
        "designation": "Senior Growth Marketing Manager",
        "salary": 96000,
        "joining_date": "2022-04-12",
        "status": "Active",
        "address": "880 Market Street, San Francisco, CA",
    },
    {
        "id": "EMP-1005",
        "full_name": "David Chen",
        "email": "david.chen@employeehub.io",
        "phone": "+1 (555) 901-2345",
        "gender": "Male",
        "dob": "1991-09-05",
        "department": "IT",
        "designation": "Senior DevOps & Security Engineer",
        "salary": 126000,
        "joining_date": "2022-09-01",
        "status": "Active",
        "address": "310 Bellevue Center, Seattle, WA",
    },
    {
        "id": "EMP-1006",
        "full_name": "Aisha Al-Mansoor",
        "email": "aisha.almansoor@employeehub.io",
        "phone": "+1 (555) 345-6789",
        "gender": "Female",
        "dob": "1995-12-03",
        "department": "Sales",
        "designation": "Enterprise Account Executive",
        "salary": 115000,
        "joining_date": "2023-01-16",
        "status": "Active",
        "address": "400 N Michigan Avenue, Chicago, IL",
    },
    {
        "id": "EMP-1007",
        "full_name": "Lucas Silva",
        "email": "lucas.silva@employeehub.io",
        "phone": "+1 (555) 789-0123",
        "gender": "Male",
        "dob": "1992-06-25",
        "department": "Operations",
        "designation": "Global Operations Lead",
        "salary": 102000,
        "joining_date": "2023-05-20",
        "status": "Active",
        "address": "1500 Congress Avenue, Austin, TX",
    },
    {
        "id": "EMP-1008",
        "full_name": "Sarah Jenkins",
        "email": "sarah.jenkins@employeehub.io",
        "phone": "+1 (555) 567-8901",
        "gender": "Female",
        "dob": "1996-03-11",
        "department": "IT",
        "designation": "Lead Full-Stack UI/UX Engineer",
        "salary": 118000,
        "joining_date": "2023-09-04",
        "status": "Active",
        "address": "250 Harvard Square, Cambridge, MA",
    },
    {
        "id": "EMP-1009",
        "full_name": "Vikram Patel",
        "email": "vikram.patel@employeehub.io",
        "phone": "+1 (555) 234-5612",
        "gender": "Male",
        "dob": "1988-07-19",
        "department": "Finance",
        "designation": "Senior Financial Controller",
        "salary": 94000,
        "joining_date": "2023-11-15",
        "status": "On Leave",
        "address": "600 Atlantic Avenue, Boston, MA",
    },
    {
        "id": "EMP-1010",
        "full_name": "Chloe Martin",
        "email": "chloe.martin@employeehub.io",
        "phone": "+1 (555) 678-9012",
        "gender": "Female",
        "dob": "1997-10-08",
        "department": "Marketing",
        "designation": "Content & Brand Strategist",
        "salary": 78000,
        "joining_date": "2024-02-01",
        "status": "Active",
        "address": "1200 Sunset Blvd, Los Angeles, CA",
    },
    {
        "id": "EMP-1011",
        "full_name": "James Wilson",
        "email": "james.wilson@employeehub.io",
        "phone": "+1 (555) 890-1234",
        "gender": "Male",
        "dob": "1985-04-29",
        "department": "Operations",
        "designation": "Logistics & Supply Chain Specialist",
        "salary": 86000,
        "joining_date": "2024-04-10",
        "status": "On Leave",
        "address": "900 Peachtree St NE, Atlanta, GA",
    },
    {
        "id": "EMP-1012",
        "full_name": "Ananya Deshmukh",
        "email": "ananya.deshmukh@employeehub.io",
        "phone": "+1 (555) 321-6549",
        "gender": "Female",
        "dob": "1994-01-14",
        "department": "IT",
        "designation": "AI Systems & ML Engineer",
        "salary": 132000,
        "joining_date": "2024-07-22",
        "status": "Active",
        "address": "100 South 2nd Street, San Jose, CA",
    },
    {
        "id": "EMP-1013",
        "full_name": "Carlos Gomez",
        "email": "carlos.gomez@employeehub.io",
        "phone": "+1 (555) 456-7892",
        "gender": "Male",
        "dob": "1990-10-17",
        "department": "Sales",
        "designation": "Regional Business Development Rep",
        "salary": 72000,
        "joining_date": "2024-10-05",
        "status": "Inactive",
        "address": "350 Brickell Ave, Miami, FL",
    },
    {
        "id": "EMP-1014",
        "full_name": "Olivia Taylor",
        "email": "olivia.taylor@employeehub.io",
        "phone": "+1 (555) 789-4321",
        "gender": "Female",
        "dob": "1995-05-30",
        "department": "HR",
        "designation": "Technical Talent Acquisition Lead",
        "salary": 89000,
        "joining_date": "2025-01-15",
        "status": "Inactive",
        "address": "500 17th St NW, Washington, DC",
    },
]

# Enrich each sample employee with initials & avatar gradient
def _enrich_employee(emp):
    enriched = dict(emp)
    enriched["initials"] = get_initials(enriched.get("full_name", ""))
    enriched["avatar_gradient"] = get_avatar_gradient(enriched.get("full_name", ""))
    # Format salary with commas for display
    enriched["salary_formatted"] = f"${int(enriched.get('salary', 0)):,}"
    return enriched

# In-Memory Storage
_EMPLOYEES = [_enrich_employee(emp) for emp in INITIAL_SAMPLE_EMPLOYEES]

def reset_to_sample_data():
    """Resets in-memory employee list to original sample data."""
    global _EMPLOYEES
    _EMPLOYEES = [_enrich_employee(emp) for emp in INITIAL_SAMPLE_EMPLOYEES]
    return len(_EMPLOYEES)

def get_all_employees(search_query=None, department=None, status=None, gender=None, sort_by=None):
    """
    Retrieve employees with optional searching, filtering, and sorting.
    """
    results = list(_EMPLOYEES)

    # 1. Search Query (ID, Name, Email, Department, Designation)
    if search_query:
        q = search_query.strip().lower()
        results = [
            emp for emp in results
            if q in emp.get("id", "").lower()
            or q in emp.get("full_name", "").lower()
            or q in emp.get("email", "").lower()
            or q in emp.get("department", "").lower()
            or q in emp.get("designation", "").lower()
        ]

    # 2. Filter: Department
    if department and department.strip() and department.lower() != "all":
        d = department.strip().lower()
        results = [emp for emp in results if emp.get("department", "").lower() == d]

    # 3. Filter: Status
    if status and status.strip() and status.lower() != "all":
        s = status.strip().lower()
        results = [emp for emp in results if emp.get("status", "").lower() == s]

    # 4. Filter: Gender
    if gender and gender.strip() and gender.lower() != "all":
        g = gender.strip().lower()
        results = [emp for emp in results if emp.get("gender", "").lower() == g]

    # 5. Sorting
    if sort_by:
        sort_by = sort_by.strip()
        if sort_by == "name_asc":
            results.sort(key=lambda x: x.get("full_name", "").lower())
        elif sort_by == "name_desc":
            results.sort(key=lambda x: x.get("full_name", "").lower(), reverse=True)
        elif sort_by == "salary_asc":
            results.sort(key=lambda x: float(x.get("salary", 0)))
        elif sort_by == "salary_desc":
            results.sort(key=lambda x: float(x.get("salary", 0)), reverse=True)
        elif sort_by == "date_asc":
            results.sort(key=lambda x: x.get("joining_date", ""))
        elif sort_by == "date_desc":
            results.sort(key=lambda x: x.get("joining_date", ""), reverse=True)
        elif sort_by == "department":
            results.sort(key=lambda x: x.get("department", "").lower())
        elif sort_by == "id_desc":
            results.sort(key=lambda x: x.get("id", ""), reverse=True)

    return results

def get_employee(employee_id):
    """Retrieve single employee by ID or return None."""
    if not employee_id:
        return None
    employee_id = str(employee_id).strip().upper()
    for emp in _EMPLOYEES:
        if emp.get("id", "").upper() == employee_id:
            return copy.deepcopy(emp)
    return None

def _generate_next_id():
    """Generate next sequential Employee ID like EMP-1015."""
    max_num = 1000
    for emp in _EMPLOYEES:
        eid = emp.get("id", "")
        if eid.startswith("EMP-"):
            try:
                num = int(eid.replace("EMP-", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"EMP-{max_num + 1}"

def add_employee(data):
    """
    Validate and add new employee to in-memory store.
    Returns (success_bool, employee_dict_or_errors).
    """
    errors = {}
    
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    gender = (data.get("gender") or "").strip()
    dob = (data.get("dob") or "").strip()
    department = (data.get("department") or "").strip()
    designation = (data.get("designation") or "").strip()
    salary = data.get("salary")
    joining_date = (data.get("joining_date") or "").strip()
    status = (data.get("status") or "Active").strip()
    address = (data.get("address") or "").strip()

    # Validations
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters."

    if not email:
        errors["email"] = "Email address is required."
    elif "@" not in email or "." not in email:
        errors["email"] = "Please enter a valid email address."
    else:
        # Check duplicate email
        for existing in _EMPLOYEES:
            if existing.get("email", "").lower() == email.lower():
                errors["email"] = "An employee with this email already exists."
                break

    if not phone:
        errors["phone"] = "Phone number is required."

    if not gender:
        errors["gender"] = "Please select gender."

    if not department:
        errors["department"] = "Please select a department."

    if not designation:
        errors["designation"] = "Designation is required."

    try:
        salary_num = float(salary)
        if salary_num < 0:
            errors["salary"] = "Salary must be a positive number."
    except (TypeError, ValueError):
        errors["salary"] = "Please enter a valid numeric salary."

    if not joining_date:
        errors["joining_date"] = "Joining date is required."

    if status not in ["Active", "Inactive", "On Leave"]:
        status = "Active"

    if errors:
        return False, errors

    # Auto-generate ID or use provided if valid
    emp_id = (data.get("id") or "").strip()
    if not emp_id or any(e["id"] == emp_id for e in _EMPLOYEES):
        emp_id = _generate_next_id()

    new_emp = {
        "id": emp_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "department": department,
        "designation": designation,
        "salary": int(salary_num) if salary_num.is_integer() else salary_num,
        "joining_date": joining_date,
        "status": status,
        "address": address,
    }
    enriched = _enrich_employee(new_emp)
    _EMPLOYEES.insert(0, enriched)
    return True, enriched

def update_employee(employee_id, data):
    """
    Update existing employee.
    Returns (success_bool, employee_dict_or_errors).
    """
    employee_id = str(employee_id).strip().upper()
    target_idx = None
    for idx, emp in enumerate(_EMPLOYEES):
        if emp.get("id", "").upper() == employee_id:
            target_idx = idx
            break

    if target_idx is None:
        return False, {"general": f"Employee {employee_id} not found."}

    errors = {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    gender = (data.get("gender") or "").strip()
    dob = (data.get("dob") or "").strip()
    department = (data.get("department") or "").strip()
    designation = (data.get("designation") or "").strip()
    salary = data.get("salary")
    joining_date = (data.get("joining_date") or "").strip()
    status = (data.get("status") or "Active").strip()
    address = (data.get("address") or "").strip()

    if not full_name:
        errors["full_name"] = "Full name is required."
    if not email:
        errors["email"] = "Email address is required."
    elif "@" not in email or "." not in email:
        errors["email"] = "Please enter a valid email address."
    else:
        # Check duplicate email in other employees
        for idx, existing in enumerate(_EMPLOYEES):
            if idx != target_idx and existing.get("email", "").lower() == email.lower():
                errors["email"] = "Another employee with this email already exists."
                break

    if not phone:
        errors["phone"] = "Phone number is required."
    if not department:
        errors["department"] = "Please select a department."
    if not designation:
        errors["designation"] = "Designation is required."

    try:
        salary_num = float(salary)
        if salary_num < 0:
            errors["salary"] = "Salary must be a positive number."
    except (TypeError, ValueError):
        errors["salary"] = "Please enter a valid numeric salary."

    if not joining_date:
        errors["joining_date"] = "Joining date is required."

    if status not in ["Active", "Inactive", "On Leave"]:
        status = "Active"

    if errors:
        return False, errors

    updated_emp = {
        "id": employee_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "department": department,
        "designation": designation,
        "salary": int(salary_num) if salary_num.is_integer() else salary_num,
        "joining_date": joining_date,
        "status": status,
        "address": address,
    }
    enriched = _enrich_employee(updated_emp)
    _EMPLOYEES[target_idx] = enriched
    return True, enriched

def delete_employee(employee_id):
    """
    Remove employee from in-memory list.
    Returns True if removed, False if not found.
    """
    global _EMPLOYEES
    employee_id = str(employee_id).strip().upper()
    initial_len = len(_EMPLOYEES)
    _EMPLOYEES = [emp for emp in _EMPLOYEES if emp.get("id", "").upper() != employee_id]
    return len(_EMPLOYEES) < initial_len

def get_dashboard_statistics():
    """
    Calculate and return complete dynamic dashboard analytics.
    """
    total = len(_EMPLOYEES)
    active = sum(1 for e in _EMPLOYEES if e.get("status") == "Active")
    on_leave = sum(1 for e in _EMPLOYEES if e.get("status") == "On Leave")
    inactive = sum(1 for e in _EMPLOYEES if e.get("status") == "Inactive")

    # Departments distribution
    dept_counts = {}
    for d_name in DEPARTMENT_META.keys():
        dept_counts[d_name] = 0
    for e in _EMPLOYEES:
        dept = e.get("department", "Other")
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    total_depts = len([k for k, v in dept_counts.items() if v > 0]) or len(DEPARTMENT_META)

    # Average salary
    salaries = [float(e.get("salary", 0)) for e in _EMPLOYEES]
    avg_salary = sum(salaries) / total if total > 0 else 0
    avg_salary_formatted = f"${int(avg_salary):,}"

    # Recent 5 employees
    recent = list(_EMPLOYEES[:5])

    return {
        "total_employees": total,
        "active_employees": active,
        "on_leave_employees": on_leave,
        "inactive_employees": inactive,
        "total_departments": total_depts,
        "average_salary": round(avg_salary, 2),
        "average_salary_formatted": avg_salary_formatted,
        "dept_counts": dept_counts,
        "status_counts": {
            "Active": active,
            "On Leave": on_leave,
            "Inactive": inactive,
        },
        "recent_employees": recent,
    }

def get_department_statistics():
    """
    Calculate per-department metrics with icons and percentages.
    """
    total_all = len(_EMPLOYEES)
    departments_data = []

    for name, meta in DEPARTMENT_META.items():
        dept_employees = [e for e in _EMPLOYEES if e.get("department") == name]
        count = len(dept_employees)
        active_count = sum(1 for e in dept_employees if e.get("status") == "Active")
        leave_count = sum(1 for e in dept_employees if e.get("status") == "On Leave")
        inactive_count = sum(1 for e in dept_employees if e.get("status") == "Inactive")

        dept_salaries = [float(e.get("salary", 0)) for e in dept_employees]
        avg_sal = sum(dept_salaries) / count if count > 0 else 0
        total_payroll = sum(dept_salaries)
        percentage = round((count / total_all * 100), 1) if total_all > 0 else 0

        departments_data.append({
            "name": name,
            "employee_count": count,
            "active_count": active_count,
            "leave_count": leave_count,
            "inactive_count": inactive_count,
            "average_salary": round(avg_sal, 2),
            "average_salary_formatted": f"${int(avg_sal):,}",
            "total_payroll": round(total_payroll, 2),
            "total_payroll_formatted": f"${int(total_payroll):,}",
            "percentage": percentage,
            "icon": meta["icon"],
            "color": meta["color"],
            "bg_color": meta["bg_color"],
            "description": meta["description"],
            "employees": dept_employees[:4],  # sample preview
        })

    return departments_data

def get_reports_statistics():
    """
    Comprehensive analytics for the Reports page.
    """
    dash_stats = get_dashboard_statistics()
    dept_stats = get_department_statistics()

    salaries = [float(e.get("salary", 0)) for e in _EMPLOYEES]
    total_payroll = sum(salaries)
    monthly_payroll = total_payroll / 12 if total_payroll > 0 else 0
    highest_salary = max(salaries) if salaries else 0
    lowest_salary = min(salaries) if salaries else 0

    # Gender breakdown
    gender_counts = {"Male": 0, "Female": 0, "Other": 0}
    for e in _EMPLOYEES:
        g = e.get("gender", "Other")
        gender_counts[g] = gender_counts.get(g, 0) + 1

    return {
        "summary": dash_stats,
        "departments": dept_stats,
        "payroll": {
            "total_annual": f"${int(total_payroll):,}",
            "monthly_payroll": f"${int(monthly_payroll):,}",
            "average_salary": dash_stats["average_salary_formatted"],
            "highest_salary": f"${int(highest_salary):,}",
            "lowest_salary": f"${int(lowest_salary):,}",
        },
        "gender_breakdown": gender_counts,
    }

def generate_csv_data():
    """
    Generate clean CSV string containing all in-memory employee data.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        "Employee ID",
        "Full Name",
        "Email",
        "Phone",
        "Gender",
        "Date of Birth",
        "Department",
        "Designation",
        "Salary (USD)",
        "Joining Date",
        "Status",
        "Address",
    ])

    for emp in _EMPLOYEES:
        writer.writerow([
            emp.get("id", ""),
            emp.get("full_name", ""),
            emp.get("email", ""),
            emp.get("phone", ""),
            emp.get("gender", ""),
            emp.get("dob", ""),
            emp.get("department", ""),
            emp.get("designation", ""),
            emp.get("salary", 0),
            emp.get("joining_date", ""),
            emp.get("status", ""),
            emp.get("address", ""),
        ])

    return output.getvalue()
