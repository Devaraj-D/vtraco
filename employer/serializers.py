from rest_framework import serializers
from .models import CustomUser

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'employee_name', 'email', 'designation', 'joining_date',
            'contact', 'salary', 'profile_picture', 'is_current_employee'
        ]

