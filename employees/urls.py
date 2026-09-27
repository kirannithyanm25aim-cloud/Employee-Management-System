"""
URL routes for the employees app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard_root'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Employees CRUD
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/add/', views.employee_add_view, name='employee_add'),
    path('employees/<str:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<str:employee_id>/edit/', views.employee_edit_view, name='employee_edit'),
    path('employees/<str:employee_id>/delete/', views.employee_delete_view, name='employee_delete'),

    # Departments, Reports & Settings
    path('departments/', views.departments_view, name='departments'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/', views.export_csv_view, name='export_csv'),
    path('settings/', views.settings_view, name='settings'),

    # Dynamic JSON APIs for frontend interaction
    path('api/employees/', views.api_employees_list, name='api_employees_list'),
    path('api/employees/<str:employee_id>/', views.api_employee_detail, name='api_employee_detail'),
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
