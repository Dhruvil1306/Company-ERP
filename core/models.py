from django.contrib.auth.models import AbstractUser
from django.db import models

# -------------------------------
# Custom User Model
# -------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('head_hr', 'Head HR'),
        ('employee', 'Employee'),  # ✅ Added Employee role
        ('manager', 'Manager'),
        ('head_manager', 'Head Manager'),
        ('sales', 'Sales'),
        ('head_sales', 'Head Sales'),
        ('support', 'Support'),
        ('head_support', 'Head Support'),
        ('tech', 'Technician'),
        ('head_tech', 'Head Technician'),
        ('account', 'Accountant'),
        ('head_account', 'Head Accountant'),
        ('customer', 'Customer'),
        ('head_customer', 'Head Customer'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# -------------------------------
# Employee Model
# -------------------------------
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            from datetime import datetime
            year_month = datetime.now().strftime("%Y%m")
            same_month_count = Employee.objects.filter(
                employee_id__startswith=year_month
            ).count() + 1
            self.employee_id = f"{year_month}{same_month_count:04d}"  # e.g., 2025100001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.employee_id}) - {self.department}"


# -------------------------------
# Payroll Model
# -------------------------------
from decimal import Decimal

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        basic = self.employee.basic_salary
        self.hra = basic * Decimal('0.20')
        self.allowances = basic * Decimal('0.10')
        self.deductions = basic * Decimal('0.05')
        self.net_salary = basic + self.hra + self.allowances - self.deductions
        super().save(*args, **kwargs)




class Team(models.Model):
    name = models.CharField(max_length=100)
    head_manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teams',
        limit_choices_to={'role': 'head_manager'}
    )
    managers = models.ManyToManyField(
        User,
        related_name='assigned_teams',
        limit_choices_to={'role': 'manager'},
        blank=True
    )
    members = models.ManyToManyField(
        User,
        related_name='team_memberships',
        limit_choices_to={'role': 'employee'},
        blank=True
    )

    def __str__(self):
        return self.name


class TeamReport(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.title}"
    


class Lead(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'sales'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.status}"