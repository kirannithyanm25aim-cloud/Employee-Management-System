"""
Django Views for Employee Hub application.
Handles page rendering and JSON API endpoints using the in-memory service.
"""
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from . import services

# ---------------------------------------------------------
# Web Page Views
# ---------------------------------------------------------

def dashboard_view(request):
    """Render modern SaaS dashboard with dynamic statistics and charts."""
    stats = services.get_dashboard_statistics()
    departments = services.get_department_statistics()
    context = {
        "page_title": "Dashboard",
        "active_nav": "dashboard",
        "stats": stats,
        "departments": departments,
        # Chart data formatted for direct JavaScript consumption
        "dept_labels_json": json.dumps(list(stats["dept_counts"].keys())),
        "dept_data_json": json.dumps(list(stats["dept_counts"].values())),
        "status_labels_json": json.dumps(list(stats["status_counts"].keys())),
        "status_data_json": json.dumps(list(stats["status_counts"].values())),
    }
    return render(request, "dashboard.html", context)


def employee_list_view(request):
    """Render employee directory with search, filter, and sorting."""
    search_query = request.GET.get("q", "")
    department = request.GET.get("department", "all")
    status = request.GET.get("status", "all")
    gender = request.GET.get("gender", "all")
    sort_by = request.GET.get("sort_by", "name_asc")

    employees = services.get_all_employees(
        search_query=search_query,
        department=department,
        status=status,
        gender=gender,
        sort_by=sort_by,
    )

    context = {
        "page_title": "Employees Directory",
        "active_nav": "employees",
        "employees": employees,
        "total_count": len(employees),
        "search_query": search_query,
        "selected_department": department,
        "selected_status": status,
        "selected_gender": gender,
        "selected_sort": sort_by,
        "departments": list(services.DEPARTMENT_META.keys()),
    }
    return render(request, "employees.html", context)


def employee_detail_view(request, employee_id):
    """Render comprehensive single employee profile."""
    employee = services.get_employee(employee_id)
    if not employee:
        messages.error(request, f"Employee '{employee_id}' was not found.")
        return redirect("employee_list")

    # Get department metadata
    dept_meta = services.DEPARTMENT_META.get(employee.get("department", "IT"), {})

    context = {
        "page_title": f"{employee['full_name']} | Employee Profile",
        "active_nav": "employees",
        "employee": employee,
        "dept_meta": dept_meta,
    }
    return render(request, "employee_detail.html", context)


def employee_add_view(request):
    """Create a new employee with live validation and error handling."""
    if request.method == "POST":
        # Check if JSON payload (AJAX) or Form-encoded
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except ValueError:
                data = {}
        else:
            data = request.POST.dict()

        success, result = services.add_employee(data)

        if success:
            messages.success(request, "Employee added successfully!")
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({"success": True, "message": "Employee added successfully!", "employee": result})
            return redirect("employee_list")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({"success": False, "errors": result}, status=400)
            
            for field, err in result.items():
                messages.error(request, f"{err}")
            
            context = {
                "page_title": "Add New Employee",
                "active_nav": "employee_add",
                "form_data": data,
                "errors": result,
                "departments": list(services.DEPARTMENT_META.keys()),
                "is_edit": False,
            }
            return render(request, "employee_form.html", context)

    # GET request
    context = {
        "page_title": "Add New Employee",
        "active_nav": "employee_add",
        "form_data": {
            "status": "Active",
            "gender": "Male",
            "department": "IT",
        },
        "errors": {},
        "departments": list(services.DEPARTMENT_META.keys()),
        "is_edit": False,
    }
    return render(request, "employee_form.html", context)


def employee_edit_view(request, employee_id):
    """Edit existing employee details."""
    employee = services.get_employee(employee_id)
    if not employee:
        messages.error(request, f"Employee '{employee_id}' not found.")
        return redirect("employee_list")

    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except ValueError:
                data = {}
        else:
            data = request.POST.dict()

        success, result = services.update_employee(employee_id, data)

        if success:
            messages.success(request, "Employee details updated successfully!")
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({"success": True, "message": "Employee details updated successfully!", "employee": result})
            return redirect("employee_detail", employee_id=employee_id)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({"success": False, "errors": result}, status=400)
            
            for field, err in result.items():
                messages.error(request, f"{err}")
            
            context = {
                "page_title": f"Edit {employee['full_name']}",
                "active_nav": "employees",
                "employee": employee,
                "form_data": data,
                "errors": result,
                "departments": list(services.DEPARTMENT_META.keys()),
                "is_edit": True,
            }
            return render(request, "employee_form.html", context)

    # GET request
    context = {
        "page_title": f"Edit {employee['full_name']}",
        "active_nav": "employees",
        "employee": employee,
        "form_data": employee,
        "errors": {},
        "departments": list(services.DEPARTMENT_META.keys()),
        "is_edit": True,
    }
    return render(request, "employee_form.html", context)


@require_http_methods(["POST", "DELETE"])
def employee_delete_view(request, employee_id):
    """Safely delete employee with confirmation handling."""
    success = services.delete_employee(employee_id)

    if success:
        messages.success(request, "Employee removed successfully.")
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
            return JsonResponse({"success": True, "message": "Employee removed successfully."})
    else:
        messages.error(request, f"Employee '{employee_id}' could not be deleted or was not found.")
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
            return JsonResponse({"success": False, "message": "Employee not found."}, status=404)

    return redirect("employee_list")


def departments_view(request):
    """Render departments showcase with dynamic member count & metrics."""
    departments = services.get_department_statistics()
    stats = services.get_dashboard_statistics()

    context = {
        "page_title": "Departments",
        "active_nav": "departments",
        "departments": departments,
        "total_employees": stats["total_employees"],
    }
    return render(request, "departments.html", context)


def reports_view(request):
    """Render executive reports and analytical breakdowns."""
    report_data = services.get_reports_statistics()

    # Pre-serialize chart datasets
    dept_names = [d["name"] for d in report_data["departments"]]
    dept_counts = [d["employee_count"] for d in report_data["departments"]]
    dept_salaries = [d["average_salary"] for d in report_data["departments"]]

    context = {
        "page_title": "Workforce Reports",
        "active_nav": "reports",
        "report": report_data,
        "dept_names_json": json.dumps(dept_names),
        "dept_counts_json": json.dumps(dept_counts),
        "dept_salaries_json": json.dumps(dept_salaries),
        "status_labels_json": json.dumps(list(report_data["summary"]["status_counts"].keys())),
        "status_data_json": json.dumps(list(report_data["summary"]["status_counts"].values())),
    }
    return render(request, "reports.html", context)


def export_csv_view(request):
    """Generate and download runtime CSV export of all employees."""
    csv_data = services.generate_csv_data()
    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="employeehub_report.csv"'
    return response


def settings_view(request):
    """Render user and application settings."""
    if request.method == "POST" and request.POST.get("action") == "reset_sample_data":
        count = services.reset_to_sample_data()
        messages.success(request, f"Data restored to {count} sample employees successfully.")
        return redirect("settings")

    context = {
        "page_title": "Settings",
        "active_nav": "settings",
        "total_employees": len(services.get_all_employees()),
    }
    return render(request, "settings.html", context)


# ---------------------------------------------------------
# Dynamic JSON API Endpoints (AJAX Support)
# ---------------------------------------------------------

def api_employees_list(request):
    """JSON API to fetch filtered/sorted employees dynamically."""
    search_query = request.GET.get("q", "")
    department = request.GET.get("department", "all")
    status = request.GET.get("status", "all")
    gender = request.GET.get("gender", "all")
    sort_by = request.GET.get("sort_by", "name_asc")

    employees = services.get_all_employees(
        search_query=search_query,
        department=department,
        status=status,
        gender=gender,
        sort_by=sort_by,
    )
    return JsonResponse({
        "success": True,
        "count": len(employees),
        "employees": employees,
    })


def api_employee_detail(request, employee_id):
    """JSON API to get single employee details."""
    emp = services.get_employee(employee_id)
    if not emp:
        return JsonResponse({"success": False, "message": "Employee not found."}, status=404)
    return JsonResponse({"success": True, "employee": emp})


def api_dashboard_stats(request):
    """JSON API to get dynamic stats for charts and KPI cards."""
    stats = services.get_dashboard_statistics()
    return JsonResponse({"success": True, "stats": stats})
