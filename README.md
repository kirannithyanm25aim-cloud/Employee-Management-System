# 🚀 EMPLOYEE HUB
### Smart Employee Management System

A modern, attractive, and responsive **Employee Management System (EMS)** web application designed with a sleek SaaS aesthetic (Dark Navy, Electric Blue/Purple gradient accents, glassmorphic cards, smooth animations, and responsive layout).

Built strictly with **Python and Django** using a **Zero-Database (100% In-Memory)** architecture.

---

## ✨ Highlights & Architecture

* **Zero Database**: No SQLite, MySQL, PostgreSQL, or ORM models.
* **In-Memory Python Service**: Managed in `employees/services.py` with Python dictionaries and lists.
* **Complete Runtime CRUD**: Add, View, Edit, and Delete employees seamlessly during runtime.
* **Modern SaaS UI**: Glassmorphism cards, animated statistics, dark/light theme switch, responsive sidebar, and micro-interactions.
* **Dynamic Analytics**: Live Chart.js department distribution charts, workforce status donuts, dual-axis salary metrics, and CSV export.
* **No Database Migrations**: Starts immediately with `python manage.py runserver` without requiring `migrate` or `makemigrations`.

---

## 🗂️ Project Structure

```
Django-1/
│
├── manage.py                     # Django management utility
├── test_suite.py                 # Automated verification test suite
├── README.md                     # Documentation
│
├── employee_management/          # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py               # Zero-database & signed-cookie session config
│   ├── urls.py                   # Root URL dispatcher
│   ├── wsgi.py                   # WSGI deployment gateway
│   └── asgi.py                   # ASGI gateway
│
├── employees/                    # Core Application
│   ├── __init__.py
│   ├── apps.py                   # App configuration
│   ├── services.py               # In-memory data store, CRUD, sample data & stats
│   ├── views.py                  # Page view controllers & JSON API endpoints
│   └── urls.py                   # Employee Hub URL routing
│
├── templates/                    # Modern HTML5 Templates
│   ├── base.html                 # Main layout, sidebar, topbar, modal & toasts
│   ├── dashboard.html            # SaaS Dashboard with KPIs and Chart.js
│   ├── employees.html            # Employees Directory (Table & Grid Views)
│   ├── employee_detail.html      # Comprehensive Employee Profile Card
│   ├── employee_form.html        # Add / Edit form with Live Profile Preview
│   ├── departments.html          # Department showcase & progress metrics
│   ├── reports.html              # Executive reports, charts & CSV download
│   └── settings.html             # Theme toggle, admin profile & data reset
│
└── static/                       # Static Assets
    ├── css/
    │   └── style.css             # Glassmorphism, animations, theme variables
    └── js/
        └── app.js                # Theme switcher, search, filters, modals, toasts
```

---

## 🛠️ Features Breakdown

### 1. Dashboard (`/` or `/dashboard/`)
* **Welcome Hero**: Personalized greeting with quick action buttons.
* **Statistic Cards**: Total Employees, Active, On Leave, Inactive, Total Departments, and Average Salary.
* **Interactive Charts**:
  * *Employee Distribution by Department* (bar chart).
  * *Workforce Status* (Active vs On Leave vs Inactive doughnut chart).
* **Department Overview**: Progress indicators calculating percentage share of workforce.
* **Recent Employees**: Quick-view table of the latest additions with avatar initials and status badges.

### 2. Employee Directory (`/employees/`)
* **Responsive Layouts**: Toggle between **Table View** and **Grid Cards View**.
* **Instant Live Search**: Search across Employee ID, Full Name, Email, Department, and Designation.
* **Multi-Filters**: Filter simultaneously by Department, Status (Active/On Leave/Inactive), and Gender.
* **Sorting**: Sort by Name (A-Z, Z-A), Salary (High-Low, Low-High), Joining Date (Newest, Oldest), or Department.
* **Empty State**: Friendly illustration and filter reset button when 0 results match.

### 3. CRUD Operations
* **Add Employee (`/employees/add/`)**: 2-column layout with validation and an interactive **Live Profile Preview card** that dynamically updates avatar initials, gradient, role, and salary as you type.
* **View Profile (`/employees/<id>/`)**: Dedicated profile showcasing personal, contact, job, and compensation information.
* **Edit Profile (`/employees/<id>/edit/`)**: Pre-populated form to update employee records in memory.
* **Delete Employee (`/employees/<id>/delete/`)**: Protected by a confirmation modal preventing accidental deletions.

### 4. Departments (`/departments/`)
* Detailed cards for all 6 organizational units: **IT**, **HR**, **Finance**, **Marketing**, **Sales**, and **Operations**.
* Shows active/leave/inactive counts, average salary, total payroll, and percentage share.
* Direct link to filter the employee directory by that specific department.

### 5. Workforce Reports & CSV Export (`/reports/`)
* High-level financial KPIs: Total Workforce, Annual Payroll Run-Rate, Monthly Payroll, and Average Compensation.
* **Dual-Axis Chart**: Compares Department Headcount with Average Salary.
* **Demographic Breakdown**: Gender diversity tracking.
* **CSV Export**: Immediate download of all in-memory data as a clean CSV file (`/reports/export/`).

### 6. Settings (`/settings/`)
* **Appearance**: Switch between **Dark Navy (Default)** and **Clean Light** modes with instant browser persistence.
* **Notification Preferences**: Toggles for email and status update alerts.
* **Admin Profile**: Custom admin display name and email.
* **Sample Data Reset**: Restore the original 14 realistic sample records with a single click.

---

## 💻 Installation & Running Locally

### Step 1: Verify Python & Django
Ensure Python 3.10+ is installed:
```bash
python --version
```
Install Django (if not already installed):
```bash
pip install django
```

### Step 2: Run the Application
From the project root (`Django-1/`), run:
```bash
python manage.py runserver
```

*(Note: There is no need to run `makemigrations` or `migrate` because there is no database).*

### Step 3: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 🧪 Automated Test Suite

A comprehensive test suite is included in `test_suite.py` to verify all views, CRUD operations, APIs, search filters, and CSV downloads:
```bash
python test_suite.py
```
Expected output:
```
=== Running Employee Hub Test Suite ===
[PASS] Dashboard view OK
[PASS] Employees list view OK
[PASS] Add Employee validation OK
[PASS] Add Employee success OK (Created ID: EMP-1015)
[PASS] View Employee Detail OK (EMP-1015)
[PASS] Edit Employee OK (EMP-1015)
[PASS] Delete Employee OK (EMP-1015)
[PASS] Filter by Department OK (4 IT employees)
[PASS] Filter by Status OK (10 Active employees)
[PASS] Search by Name OK (Found Alexander Wright)
[PASS] Departments view OK
[PASS] Reports view OK
[PASS] CSV Export OK (Valid headers and data)
[PASS] Settings view OK
[PASS] Settings reset sample data OK (Restored to 14 records)
[PASS] API /api/employees/ OK
[PASS] API /api/dashboard/stats/ OK

ALL TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.
```
