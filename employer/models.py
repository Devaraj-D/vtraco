from django.db import models
from django.conf import settings
# Create your models here.

class Salary(models.Model):
    ATTENDANCE_TYPE_CHOICES = [
        ('full_day', 'Full Day'),
        ('half_day', 'Half Day'),
        ('absent', 'Absent'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salaries')
    date = models.DateField()
    attendance_type = models.CharField(
        max_length=10,
        choices=ATTENDANCE_TYPE_CHOICES,
        default='full_day'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.BooleanField(default=False)  # False = not paid, True = paid

    def _str_(self):
        return f"{self.user.username} - {self.date} - {self.attendance_type}"
