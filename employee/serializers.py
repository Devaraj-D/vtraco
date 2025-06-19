from rest_framework import serializers
from .models import Attendance, EmployeeRequest, Salary, Notification
from users.models import CustomUser

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['user']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'employee_name', 'email', 'contact', 'company_name',
            'designation', 'dob', 'salary', 'joining_date', 'created_at'
        ]

class EmployeeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequest
        fields = ['id', 'user', 'request_type', 'reason', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['id', 'date', 'attendance_type', 'salary', 'status']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
