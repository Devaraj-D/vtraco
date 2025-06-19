from django.db import models
from django.conf import settings
from users.models import CustomUser

class Attendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employee_attendances')
    
    date = models.DateField()
    day = models.CharField(max_length=20)
    login_time = models.TimeField()
    logout_time = models.TimeField(null=True, blank=True)
    eod_report = models.TextField(blank=True)
    document = models.FileField(upload_to='attendance_docs/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Salary(models.Model):
    ATTENDANCE_TYPE_CHOICES = [
        ('full_day', 'Full Day'),
        ('half_day', 'Half Day'),
        ('absent', 'Absent'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employee_salaries')
    
    date = models.DateField()
    attendance_type = models.CharField(
        max_length=10,
        choices=ATTENDANCE_TYPE_CHOICES,
        default='full_day'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.BooleanField(default=False)  # False = not paid, True = paid

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.attendance_type}"
    
class EmployeeRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('leave', 'Leave Permission'),
        ('wfh', 'Work From Home Permission'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.request_type} - {self.status}"
    
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"Notification for {self.user.email}"
    

class Attendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_from_users')
    date = models.DateField()
    day = models.CharField(max_length=20)
    login_time = models.TimeField()
    logout_time = models.TimeField(null=True, blank=True)
    eod_report = models.TextField(blank=True)
    document = models.FileField(upload_to='attendance_docs/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"