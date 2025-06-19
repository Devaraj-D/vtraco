from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Salary
from users.models import CustomUser,Attendance
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

# If you have a utility for generating passwords and sending emails
# from your_app.utils import generate_password, send_invitation_email  # Replace with actual utility path


User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_employees(request):
    employer = request.user

    if employer.role_id != 2:
        return Response({"detail": "Only employers can view employees."}, status=status.HTTP_403_FORBIDDEN)

    employees = User.objects.filter(role_id=3, company_name=employer.company_name)
    employee_data = [
        {
            "id": emp.id,
            "employee_name": emp.employee_name,
            "email": emp.email,
            "contact": emp.contact,
            "designation": emp.designation,
            "dob": emp.dob,
            "salary": emp.salary,
            "joining_date": emp.joining_date,
        }
        for emp in employees
    ]
    return Response({"status": "success", "employees": employee_data}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_employee(request, employee_id):
    employer = request.user

    if employer.role_id != 2:
        return Response({"detail": "Only employers can delete employees."}, status=status.HTTP_403_FORBIDDEN)

    try:
        employee = User.objects.get(id=employee_id, role_id=3, company_name=employer.company_name)
        employee.delete()
        return Response({"status": "success", "message": "Employee deleted successfully."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"status": "error", "message": "Employee not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_employee(request, employee_id):
    employer = request.user

    if employer.role_id != 2:
        return Response({"detail": "Only employers can update employees."}, status=status.HTTP_403_FORBIDDEN)

    try:
        print(employee_id)
        employee = User.objects.get(id=employee_id, role_id=3, company_name=employer.company_name)

        employee.employee_name = request.data.get('employee_name', employee.employee_name)
        employee.contact = request.data.get('phone', employee.contact)
        employee.designation = request.data.get('designation', employee.designation)
        employee.dob = request.data.get('dob', employee.dob)
        employee.salary = request.data.get('salary', employee.salary)
        employee.joining_date = request.data.get('joining_date', employee.joining_date)

        employee.save()

        return Response({
            "status": "success",
            "message": "Employee details updated successfully."
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist as e:
        print(e)
        return Response({"status": "error", "message": "Employee not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_salary(request, id):
    try:
        try:
            salary_record = Salary.objects.get(id=id)
        except Salary.DoesNotExist:
            return Response({"error": "Salary record not found."}, status=404)

        salary_record.attendance_type = request.data.get("attendance_type", salary_record.attendance_type)
        salary_record.salary = request.data.get("salary", salary_record.salary)
        salary_record.status = request.data.get("status", salary_record.status)

        salary_record.save()

        return Response({
            "message": "Salary record updated successfully.",
            "data": {
                "id": salary_record.id,
                "user": salary_record.user.username,
                "date": str(salary_record.date),
                "attendance_type": salary_record.attendance_type,
                "salary": str(salary_record.salary),
                "status": salary_record.status
            }
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_employees(request):
    try:
        employer = request.user
        if employer.role_id != 2:
            return Response({'error': 'Only employers can access this endpoint'}, status=403)

        company_name = employer.company_name
        employees = CustomUser.objects.filter(company_name=company_name, role_id=3)

        data = []
        for emp in employees:
            present = Attendance.objects.filter(user=emp, login_time__isnull=False, logout_time__isnull=False).count()
            total_days = Attendance.objects.filter(user=emp).count()
            absent = total_days - present
            attendance_percent = round((present / total_days) * 100, 2) if total_days else 0.0

            emp_data = {
                'name': emp.employee_name,
                'email': emp.email,
                'designation': emp.designation,
                'join_date': emp.joining_date,
                'phone': emp.contact,
                'present': present,
                'absent': absent,
                'attendance_percent': attendance_percent,
                'status': 'Current' if emp.is_current_employee else 'Former',
                'profile_picture': request.build_absolute_uri(emp.profile_picture.url) if emp.profile_picture else None
            }
            data.append(emp_data)

        return Response({'employees': data})

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
