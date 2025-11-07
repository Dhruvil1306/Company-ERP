from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------
    # Authentication
    # -------------------------------
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # -------------------------------
    # ERP Dashboards (prefixed /erp/)
    # -------------------------------
    path('erp/admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('erp/hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('erp/head_hr/dashboard/', views.head_hr_dashboard, name='head_hr_dashboard'),
    path('erp/manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('erp/head_manager/dashboard/', views.head_manager_dashboard, name='head_manager_dashboard'),
    path('erp/sales/dashboard/', views.sales_dashboard, name='sales_dashboard'),
    path('erp/head_sales/dashboard/', views.head_sales_dashboard, name='head_sales_dashboard'),
    path('erp/support/dashboard/', views.support_dashboard, name='support_dashboard'),
    path('erp/head_support/dashboard/', views.head_support_dashboard, name='head_support_dashboard'),
    path('erp/tech/dashboard/', views.tech_dashboard, name='tech_dashboard'),
    path('erp/head_tech/dashboard/', views.head_tech_dashboard, name='head_tech_dashboard'),
    path('erp/account/dashboard/', views.account_dashboard, name='account_dashboard'),
    path('erp/head_account/dashboard/', views.head_account_dashboard, name='head_account_dashboard'),
    path('erp/customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('erp/head_customer/dashboard/', views.head_customer_dashboard, name='head_customer_dashboard'),

    # -------------------------------
    # Unauthorized page
    # -------------------------------
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    # -------------------------------
    # ERP User Management by Admin
    # -------------------------------
    path('erp/admin/users/', views.manage_users, name='manage_users'),
    path('erp/admin/users/add/', views.add_user, name='add_user'),
    path('erp/admin/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('erp/admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # -------------------------------
    # Profile (global for all roles)
    # -------------------------------
    path('profile/', views.profile, name='profile'),

    # -------------------------------
    # Reports
    # -------------------------------
    path('erp/admin/reports/', views.admin_reports, name='admin_reports'),
    path('erp/hr/reports/', views.hr_reports, name='hr_reports'),



    # HR Employee Management
    path('erp/hr/employees/', views.manage_employees, name='manage_employees'),
    path('erp/hr/employees/add/', views.add_employee, name='add_employee'),
    path('erp/hr/employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('erp/hr/employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),


    # HR Payroll Management
    path('erp/hr/payrolls/', views.manage_payrolls, name='manage_payrolls'),
    path('erp/hr/payrolls/add/', views.add_payroll, name='add_payroll'),
    path('erp/hr/payrolls/edit/<int:payroll_id>/', views.edit_payroll, name='edit_payroll'),
    path('erp/hr/payrolls/delete/<int:payroll_id>/', views.delete_payroll, name='delete_payroll'),
    path('erp/head_manager/assign-manager/', views.assign_manager, name='assign_manager'),
    path('erp/head_manager/create-team/', views.create_team, name='create_team'),
    path('erp/head_manager/manage-teams/', views.manage_teams, name='manage_teams'),
    path('erp/head_manager/edit-team/<int:team_id>/', views.edit_team, name='edit_team'),
    path('erp/head_manager/delete-team/<int:team_id>/', views.delete_team, name='delete_team'),     

    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/assign-task/<int:team_id>/', views.assign_task, name='assign_task'),
    path('manager/tasks/', views.manager_tasks, name='manager_tasks'),
    path('sales/leads/', views.sales_leads, name='sales_leads'),
    path('sales/leads/', views.sales_leads_list, name='sales_leads_list'),

    path('sales/lead/update/<int:lead_id>/', views.update_lead, name='update_lead'),
    path('sales/add-lead/', views.add_lead, name='add_lead'),






]
