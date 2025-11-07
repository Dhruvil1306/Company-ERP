from django.contrib import admin
from .models import Team, TeamReport, User, Employee, Payroll

# ------------------ USER ------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


# ------------------ EMPLOYEE ------------------
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'employee_id', 'department', 'designation', 'basic_salary')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id', 'department')

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    full_name.admin_order_field = 'user__first_name'
    full_name.short_description = 'Full Name'


# ------------------ PAYROLL ------------------
@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee_full_name', 'month', 'year', 'net_salary', 'created_at')
    list_filter = ('month', 'year')
    search_fields = ('employee__user__username', 'employee__employee_id')

    def employee_full_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}"
    employee_full_name.short_description = 'Employee'


# ------------------ TEAM ------------------
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'head_manager', 'managers_list', 'members_list')
    list_filter = ('head_manager',)
    search_fields = ('name', 'head_manager__username')
    filter_horizontal = ('managers', 'members')  # Multi-select widget

    def managers_list(self, obj):
        return ", ".join([m.username for m in obj.managers.all()])
    managers_list.short_description = 'Managers'

    def members_list(self, obj):
        return ", ".join([m.username for m in obj.members.all()])
    members_list.short_description = 'Members'


# ------------------ TEAM REPORT ------------------
@admin.register(TeamReport)
class TeamReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'team_name', 'head_manager', 'created_at')
    list_filter = ('team', 'created_at')
    search_fields = ('title', 'team__name', 'team__head_manager__username')

    def team_name(self, obj):
        return obj.team.name
    team_name.short_description = 'Team'

    def head_manager(self, obj):
        return obj.team.head_manager.username
    head_manager.short_description = 'Head Manager'


from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'assigned_to', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to')
    search_fields = ('name', 'email', 'phone', 'company')
