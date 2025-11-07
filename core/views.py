import datetime
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from functools import wraps

from core.forms import EmployeeForm, LeadForm, UserForm

User = get_user_model()

# --------------------------------
# Helper Decorator for Role-Based Access
# --------------------------------
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return redirect('unauthorized')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --------------------------------
# Authentication
# --------------------------------
def login_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirect to role-based dashboard
            return redirect(f'/erp/{user.role}/dashboard/')
        else:
            error = 'Invalid credentials'
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

# --------------------------------
# Unauthorized page
# --------------------------------
def unauthorized(request):
    return render(request, 'unauthorized.html')

# --------------------------------
# Dashboards
# --------------------------------
@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')

@login_required
@role_required(['hr'])
def hr_dashboard(request):
    return render(request, 'hr/dashboard.html')

@login_required
def head_hr_dashboard(request):
    if request.user.role != 'head_hr':
        return redirect('unauthorized')

    total_employees = Employee.objects.count()
    total_payrolls = Payroll.objects.count()
    total_reports = 0  # You can calculate actual pending HR reports here

    context = {
        'total_employees': total_employees,
        'total_payrolls': total_payrolls,
        'total_reports': total_reports,
    }
    return render(request, 'head_hr/dashboard.html', context)


@login_required
def manager_dashboard(request):
    if request.user.role != 'manager':
        return redirect('unauthorized')

    # Teams assigned to this manager
    teams = request.user.assigned_teams.all()  # ManyToManyField from Team model

    # Count total team members and reports
    total_team_members = sum(team.members.count() for team in teams)
    total_reports = TeamReport.objects.filter(team__in=teams).count()

    context = {
        'teams': teams,
        'total_team_members': total_team_members,
        'total_reports': total_reports,
    }
    return render(request, 'manager/dashboard.html', context)


@login_required
def assign_task(request, team_id):
    if request.user.role != 'manager':
        return redirect('unauthorized')

    team = get_object_or_404(Team, id=team_id, managers=request.user)
    members = team.members.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        TeamReport.objects.create(team=team, title=title, description=description)
        messages.success(request, f"Task '{title}' assigned to team '{team.name}'!")
        return redirect('manager_dashboard')

    context = {
        'team': team,
        'members': members,
    }
    return render(request, 'manager/assign_task.html', context)


@login_required
def manager_tasks(request):
    if request.user.role != 'manager':
        return redirect('unauthorized')

    teams = request.user.assigned_teams.all()
    tasks = TeamReport.objects.filter(team__in=teams).order_by('-created_at')

    context = {'tasks': tasks}
    return render(request, 'manager/tasks.html', context)


@login_required
def head_manager_dashboard(request):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    total_teams = Team.objects.filter(head_manager=request.user).count()
    total_managers = User.objects.filter(role='manager', assigned_teams__head_manager=request.user).count()
    total_reports = sum(team.reports.count() for team in Team.objects.filter(head_manager=request.user))

    context = {
        'total_teams': total_teams,
        'total_managers': total_managers,
        'total_reports': total_reports,
    }
    return render(request, 'head_manager/dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, User  # adjust imports to your app

@login_required
def assign_manager(request):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    # Teams under this Head Manager
    teams = Team.objects.filter(head_manager=request.user)
    # Available managers
    managers = User.objects.filter(role='manager')

    if request.method == 'POST':
        team_id = request.POST.get('team')
        manager_ids = request.POST.getlist('managers')

        team = get_object_or_404(Team, id=team_id, head_manager=request.user)
        selected_managers = User.objects.filter(id__in=manager_ids, role='manager')
        team.managers.set(selected_managers)

        messages.success(request, f"Managers assigned to team '{team.name}' successfully!")
        return redirect('manage_teams')  # redirect to a view that lists all teams

    context = {
        'teams': teams,
        'managers': managers,
    }
    return render(request, 'head_manager/assign_manager.html', context)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Lead

@login_required
def sales_dashboard(request):
    if request.user.role != 'sales':
        return redirect('unauthorized')

    # Example metrics
    total_leads = Lead.objects.filter(assigned_to=request.user).count()
    open_leads = Lead.objects.filter(assigned_to=request.user, status='Open').count()
    closed_leads = Lead.objects.filter(assigned_to=request.user, status='Closed').count()

    context = {
        'total_leads': total_leads,
        'open_leads': open_leads,
        'closed_leads': closed_leads,
    }
    return render(request, 'sales/dashboard.html', context)


@login_required
def sales_leads(request):
    if request.user.role != 'sales':
        return redirect('unauthorized')

    leads = Lead.objects.filter(assigned_to=request.user).order_by('-created_at')
    return render(request, 'sales/leads.html', {'leads': leads})

@login_required
def add_lead(request):
    if request.user.role != 'sales':
        return redirect('unauthorized')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        status = request.POST.get('status', 'Open')

        Lead.objects.create(
            name=name,
            email=email,
            phone=phone,
            status=status,
            assigned_to=request.user
        )
        messages.success(request, f"Lead '{name}' added successfully!")
        return redirect('sales_dashboard')

    return render(request, 'sales/add_lead.html')

@login_required
def update_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.user.role != 'sales' or lead.assigned_to != request.user:
        return redirect('unauthorized')

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lead '{lead.name}' updated successfully!")
            return redirect('sales_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = LeadForm(instance=lead)

    return render(request, 'sales/update_lead.html', {'form': form, 'lead': lead})

# core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Lead

@login_required
def sales_leads_list(request):
    if request.user.role != 'sales':
        return redirect('unauthorized')

    leads = Lead.objects.filter(assigned_to=request.user)
    context = {'leads': leads}
    return render(request, 'sales/leads_list.html', context)


@login_required
@role_required(['head_sales'])
def head_sales_dashboard(request):
    return render(request, 'head_sales/dashboard.html')

@login_required
@role_required(['support'])
def support_dashboard(request):
    return render(request, 'support/dashboard.html')

@login_required
@role_required(['head_support'])
def head_support_dashboard(request):
    return render(request, 'head_support/dashboard.html')

@login_required
@role_required(['tech'])
def tech_dashboard(request):
    return render(request, 'tech/dashboard.html')

@login_required
@role_required(['head_tech'])
def head_tech_dashboard(request):
    return render(request, 'head_tech/dashboard.html')

@login_required
@role_required(['account'])
def account_dashboard(request):
    return render(request, 'account/dashboard.html')

@login_required
@role_required(['head_account'])
def head_account_dashboard(request):
    return render(request, 'head_account/dashboard.html')

@login_required
@role_required(['customer'])
def customer_dashboard(request):
    return render(request, 'customer/dashboard.html')

@login_required
@role_required(['head_customer'])
def head_customer_dashboard(request):
    return render(request, 'head_customer/dashboard.html')

# --------------------------------
# Admin: User Management
# --------------------------------
@login_required
@role_required(['admin'])
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
@role_required(['admin'])
def add_user(request):
    roles = [
        'hr', 'head_hr', 'manager', 'head_manager', 'sales','employee', 'head_sales',
        'support', 'head_support', 'tech', 'head_tech', 'account', 'head_account',
        'customer', 'head_customer'
    ]
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = User.objects.create_user(username=username, password=password, role=role)
        return redirect('manage_users')
    return render(request, 'admin/add_user.html', {'roles': roles})

@login_required
@role_required(['admin'])
def edit_user(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    roles = [
        'hr', 'head_hr', 'manager', 'head_manager', 'sales','employee', 'head_sales',
        'support', 'head_support', 'tech', 'head_tech', 'account', 'head_account',
        'customer', 'head_customer'
    ]
    if request.method == 'POST':
        user_obj.username = request.POST.get('username')
        user_obj.role = request.POST.get('role')
        if request.POST.get('password'):
            user_obj.set_password(request.POST.get('password'))
        user_obj.save()
        return redirect('manage_users')
    return render(request, 'admin/edit_user.html', {'user_obj': user_obj, 'roles': roles})

@login_required
@role_required(['admin'])
def delete_user(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    user_obj.delete()
    return redirect('manage_users')



@login_required
@role_required(['admin'])
def add_employee(request):
    from .models import Employee
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(employee__isnull=True)  # Only users without employee
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_obj = User.objects.get(id=user_id)
        employee = Employee(
            user=user_obj,
            department=request.POST.get('department'),
            designation=request.POST.get('designation'),
            contact_number=request.POST.get('contact_number'),
            date_of_joining=request.POST.get('date_of_joining'),
            photo=request.FILES.get('photo'),
            basic_salary=request.POST.get('basic_salary')
        )
        employee.save()
        return redirect('manage_users')
    return render(request, 'hr/add_employee.html', {'users': users})


@login_required
def profile(request):
    user = request.user
    employee = getattr(user, 'employee', None)  # Get employee info if exists

    if request.method == 'POST':
        user.username = request.POST.get('username')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        user.save()

        if employee:
            employee.contact_number = request.POST.get('contact_number')
            employee.department = request.POST.get('department')
            employee.designation = request.POST.get('designation')
            if request.FILES.get('photo'):
                employee.photo = request.FILES.get('photo')
            employee.save()

        return redirect('profile')

    return render(request, 'profile.html', {'user': user, 'employee': employee})



@login_required
@role_required(['admin'])
def admin_reports(request):
    from .models import Employee, Payroll
    # Example: total employees and payroll summary
    total_employees = Employee.objects.count()
    total_payrolls = Payroll.objects.count()
    total_salary = sum([p.net_salary for p in Payroll.objects.all()])
    context = {
        'total_employees': total_employees,
        'total_payrolls': total_payrolls,
        'total_salary': total_salary
    }
    return render(request, 'admin/reports.html', context)



@login_required
@role_required(['hr'])
def hr_reports(request):
    from .models import Employee, Payroll
    employees = Employee.objects.all()
    payrolls = Payroll.objects.all()
    context = {'employees': employees, 'payrolls': payrolls}
    return render(request, 'hr/reports.html', context)


from .models import Employee, Team, TeamReport, User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def manage_employees(request):
    if request.user.role not in ['hr', 'head_hr']:
        return redirect('unauthorized')
    employees = Employee.objects.all()
    return render(request, 'hr/employee_list.html', {'employees': employees})


@login_required
def add_employee(request):
    if request.user.role not in ['hr', 'head_hr']:
        return redirect('unauthorized')

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST, request.FILES)

        if user_form.is_valid() and employee_form.is_valid():
            # Create user but enforce role as 'employee'
            user = user_form.save(commit=False)
            user.role = 'employee'  # default role
            user.save()

            # Create employee linked to user
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()

            messages.success(request, f"Employee {user.username} added successfully!")
            return redirect('manage_employees')
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        user_form = UserForm()
        employee_form = EmployeeForm()

    return render(request, 'hr/employee_form.html', {
        'user_form': user_form,
        'employee_form': employee_form
    })



@login_required
def edit_employee(request, employee_id):
    if request.user.role not in ['hr', 'head_hr']:
        return redirect('unauthorized')
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee.user.username = request.POST.get('username')
        if request.POST.get('password'):
            employee.user.set_password(request.POST.get('password'))
        employee.user.save()

        employee.department = request.POST.get('department')
        employee.designation = request.POST.get('designation')
        employee.contact_number = request.POST.get('contact_number')
        employee.basic_salary = request.POST.get('basic_salary')
        employee.save()
        return redirect('manage_employees')

    return render(request, 'hr/employee_form.html', {'employee': employee})


@login_required
def delete_employee(request, employee_id):
    if request.user.role not in ['hr', 'head_hr']:
        return redirect('unauthorized')
    employee = get_object_or_404(Employee, id=employee_id)
    employee.user.delete()  # delete user also
    return redirect('manage_employees')




from .models import Payroll, Employee
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def manage_payrolls(request):
    if request.user.role not in ['hr', 'head_hr', 'account', 'head_account']:
        return redirect('unauthorized')
    payrolls = Payroll.objects.all()
    return render(request, 'hr/payroll_list.html', {'payrolls': payrolls})

@login_required
def add_payroll(request):
    if request.user.role not in ['hr', 'head_hr', 'account', 'head_account']:
        return redirect('unauthorized')

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        month = request.POST.get('month')
        year = request.POST.get('year')
        employee = get_object_or_404(Employee, id=employee_id)

        Payroll.objects.create(employee=employee, month=month, year=year)
        return redirect('manage_payrolls')

    employees = Employee.objects.all()
    return render(request, 'hr/payroll_form.html', {'employees': employees})

@login_required
def edit_payroll(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    if request.user.role not in ['hr', 'head_hr', 'account', 'head_account']:
        return redirect('unauthorized')

    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        payroll.month = month
        payroll.year = year
        payroll.save()
        return redirect('manage_payrolls')

    employees = Employee.objects.all()
    return render(request, 'hr/payroll_form.html', {'payroll': payroll, 'employees': employees})

@login_required
def delete_payroll(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    if request.user.role not in ['hr', 'head_hr', 'account', 'head_account']:
        return redirect('unauthorized')
    payroll.delete()
    return redirect('manage_payrolls')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Team, User
from django.contrib import messages


@login_required
def create_team(request):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    employees = User.objects.filter(role='employee')

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        selected_employee_ids = request.POST.getlist('members')

        team = Team.objects.create(name=team_name, head_manager=request.user)
        if selected_employee_ids:
            team.members.set(User.objects.filter(id__in=selected_employee_ids))

        messages.success(request, f"Team '{team_name}' created successfully!")
        return redirect('head_manager_dashboard')

    context = {'employees': employees}
    return render(request, 'head_manager/create_team.html', context)



@login_required
def manage_teams(request):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    # Get all teams of this head manager
    teams = Team.objects.filter(head_manager=request.user).prefetch_related('managers')

    context = {
        'teams': teams,
    }
    return render(request, 'head_manager/manage_teams.html', context)


@login_required
def edit_team(request, team_id):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')
    
    team = get_object_or_404(Team, id=team_id, head_manager=request.user)
    managers = User.objects.filter(role='manager')

    if request.method == 'POST':
        team.name = request.POST.get('team_name')
        manager_ids = request.POST.getlist('managers')
        selected_managers = User.objects.filter(id__in=manager_ids, role='manager')
        team.managers.set(selected_managers)
        team.save()
        return redirect('manage_teams')

    context = {'team': team, 'managers': managers}
    return render(request, 'head_manager/edit_team.html', context)


@login_required
def delete_team(request, team_id):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')
    
    team = get_object_or_404(Team, id=team_id, head_manager=request.user)
    team.delete()
    return redirect('manage_teams')



@login_required
def edit_team(request, team_id):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    team = Team.objects.get(id=team_id, head_manager=request.user)
    employees = User.objects.filter(role='employee')

    if request.method == 'POST':
        team.name = request.POST.get('team_name')
        selected_members = request.POST.getlist('members')
        team.members.set(User.objects.filter(id__in=selected_members))
        team.save()
        messages.success(request, f"Team '{team.name}' updated successfully!")
        return redirect('manage_teams')

    context = {'team': team, 'employees': employees}
    return render(request, 'head_manager/edit_team.html', context)


@login_required
def delete_team(request, team_id):
    if request.user.role != 'head_manager':
        return redirect('unauthorized')

    team = Team.objects.get(id=team_id, head_manager=request.user)
    team.delete()
    messages.success(request, f"Team '{team.name}' deleted successfully!")
    return redirect('manage_teams')




from .models import Lead


@login_required
def sales_leads(request):
    if request.user.role != 'sales':
        return redirect('unauthorized')

    # Example: fetch leads assigned to this sales user
    leads = Lead.objects.filter(assigned_to=request.user).order_by('-created_at')

    context = {'leads': leads}
    return render(request, 'sales/leads.html', context)
