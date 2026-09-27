"""
Comprehensive Test Suite for Employee Hub (Zero Database).
Verifies all views, URLs, CRUD operations, APIs, search, and CSV export.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.test.client import Client
from employees import services

def run_tests():
    client = Client()
    print("=== Running Employee Hub Test Suite ===")

    # 1. Dashboard
    res = client.get('/dashboard/')
    assert res.status_code == 200, f"Dashboard failed: {res.status_code}"
    assert b"Good Morning, Admin" in res.content
    print("[PASS] Dashboard view OK")

    # 2. Employees List
    res = client.get('/employees/')
    assert res.status_code == 200, f"Employee list failed: {res.status_code}"
    assert b"Alexander Wright" in res.content
    print("[PASS] Employees list view OK")

    # 3. Add Employee (Validation failure test)
    res = client.post('/employees/add/', {})
    assert res.status_code == 200
    assert b"Full name is required" in res.content
    print("[PASS] Add Employee validation OK")

    # 4. Add Employee (Success test)
    new_data = {
        "full_name": "Jordan Peterson",
        "email": "jordan.peterson@employeehub.io",
        "phone": "+1 (555) 999-8888",
        "gender": "Male",
        "dob": "1988-03-20",
        "department": "IT",
        "designation": "Staff Infrastructure Architect",
        "salary": "155000",
        "joining_date": "2025-02-01",
        "status": "Active",
        "address": "100 Silicon Way, Palo Alto, CA",
    }
    res = client.post('/employees/add/', new_data, follow=True)
    assert res.status_code == 200
    added_emp = None
    for emp in services.get_all_employees():
        if emp["email"] == new_data["email"]:
            added_emp = emp
            break
    assert added_emp is not None, "Added employee was not found in in-memory store!"
    added_id = added_emp["id"]
    print(f"[PASS] Add Employee success OK (Created ID: {added_id})")

    # 5. View Employee Detail
    res = client.get(f'/employees/{added_id}/')
    assert res.status_code == 200
    assert b"Jordan Peterson" in res.content
    assert b"Staff Infrastructure Architect" in res.content
    print(f"[PASS] View Employee Detail OK ({added_id})")

    # 6. Edit Employee
    update_data = dict(new_data)
    update_data["designation"] = "Principal Infrastructure Architect"
    update_data["salary"] = "165000"
    res = client.post(f'/employees/{added_id}/edit/', update_data, follow=True)
    assert res.status_code == 200
    updated_emp = services.get_employee(added_id)
    assert updated_emp["designation"] == "Principal Infrastructure Architect"
    assert updated_emp["salary"] == 165000
    print(f"[PASS] Edit Employee OK ({added_id})")

    # 7. Delete Employee
    res = client.post(f'/employees/{added_id}/delete/', follow=True)
    assert res.status_code == 200
    assert services.get_employee(added_id) is None, "Employee was not deleted!"
    print(f"[PASS] Delete Employee OK ({added_id})")

    # 8. Search & Filters in Service
    it_employees = services.get_all_employees(department="IT")
    for e in it_employees:
        assert e["department"] == "IT"
    print(f"[PASS] Filter by Department OK ({len(it_employees)} IT employees)")

    active_employees = services.get_all_employees(status="Active")
    for e in active_employees:
        assert e["status"] == "Active"
    print(f"[PASS] Filter by Status OK ({len(active_employees)} Active employees)")

    search_res = services.get_all_employees(search_query="Alexander")
    assert len(search_res) >= 1
    assert search_res[0]["full_name"] == "Alexander Wright"
    print(f"[PASS] Search by Name OK (Found Alexander Wright)")

    # 9. Departments Page
    res = client.get('/departments/')
    assert res.status_code == 200
    assert b"Departments Overview" in res.content
    assert b"Headcount" in res.content
    print("[PASS] Departments view OK")

    # 10. Reports Page
    res = client.get('/reports/')
    assert res.status_code == 200
    assert b"Workforce Analytics" in res.content
    print("[PASS] Reports view OK")

    # 11. Export CSV
    res = client.get('/reports/export/')
    assert res.status_code == 200
    assert res['Content-Type'] == 'text/csv'
    csv_text = res.content.decode('utf-8')
    assert "Employee ID,Full Name,Email" in csv_text
    assert "Alexander Wright" in csv_text
    print("[PASS] CSV Export OK (Valid headers and data)")

    # 12. Settings & Reset Sample Data
    res = client.get('/settings/')
    assert res.status_code == 200
    assert b"System & User Settings" in res.content
    print("[PASS] Settings view OK")

    res = client.post('/settings/', {"action": "reset_sample_data"}, follow=True)
    assert res.status_code == 200
    assert len(services.get_all_employees()) == 14
    print("[PASS] Settings reset sample data OK (Restored to 14 records)")

    # 13. API Endpoints
    api_list = client.get('/api/employees/')
    assert api_list.status_code == 200
    data = api_list.json()
    assert data["success"] is True
    assert data["count"] == 14
    print("[PASS] API /api/employees/ OK")

    api_stats = client.get('/api/dashboard/stats/')
    assert api_stats.status_code == 200
    stats_data = api_stats.json()
    assert stats_data["success"] is True
    assert stats_data["stats"]["total_employees"] == 14
    print("[PASS] API /api/dashboard/stats/ OK")

    print("\nALL TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.")

if __name__ == '__main__':
    run_tests()
