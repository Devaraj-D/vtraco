from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance
from datetime import datetime
import calendar
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import CustomUser
from .serializers import EmployeeSerializer, EmployeeRequestSerializer, SalarySerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attendance_login(request):
    user = request.user
    date_str = request.data.get('date')
    login_time_str = request.data.get('time')

    if not date_str or not login_time_str:
        return Response({'error': 'date and time are required.'}, status=status.HTTP_400_BAD_REQUEST)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    login_time = datetime.strptime(login_time_str, "%H:%M").time()
    day = calendar.day_name[date.weekday()]

    attendance, created = Attendance.objects.get_or_create(
        user=user,
        date=date,
        defaults={'day': day, 'login_time': login_time}
    )

    if not created:
        return Response({"error": "Login already marked for this date."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "success",
        "message": "Login recorded successfully.",
        "data": {
            "date": date_str,
            "day": day,
            "login_time": login_time_str
        }
    }, status=status.HTTP_201_CREATED)



from .models import Attendance, Salary
# from users.models import User  # If needed

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def attendance_logout(request):
    user = request.user
    date_str = request.data.get('date')

    if not date_str:
        return Response({"error": "date is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        attendance = Attendance.objects.get(user=user, date=date_str)
    except Attendance.DoesNotExist:
        return Response({"error": "Login record not found for the given date."}, status=status.HTTP_404_NOT_FOUND)

    attendance.logout_time = datetime.now().time()
    attendance.eod_report = request.data.get('eod_report', '')
    if 'document' in request.FILES:
        attendance.document = request.FILES['document']

    attendance.save()

    # Save to Salary table
    try:
        # Use full_day as default or logic-based assignment
        attendance_type = 'full_day'
        calculated_salary = user.salary if hasattr(user, 'salary') else 0

        Salary.objects.update_or_create(
            user=user,
            date=attendance.date,
            defaults={
                'attendance_type': attendance_type,
                'salary': None,
                'status': False  # Not yet marked as paid
            }
        )
    except Exception as e:
        return Response({"error": f"Failed to store salary info: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "status": "success",
        "message": "Logout updated and salary entry recorded successfully."
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees(request):
    # Only employer and admin can view employee list
    if request.user.role_id not in [3]:
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

    employees = CustomUser.objects.filter(id=request.user.id, is_delete=False)
    serializer = EmployeeSerializer(employees, many=True)
    
    return Response({
        "status": "success",
        "employees": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def employee_request(request):
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Automatically attach the logged-in user

    serializer = EmployeeRequestSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Request submitted successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_salary_details(request):
    user = request.user
    salary_qs = Salary.objects.filter(user=user, status=True).order_by('-date')
    
    serializer = SalarySerializer(salary_qs, many=True)

    return Response({
        "status": "success",
        "salary_records": serializer.data
    }, status=status.HTTP_200_OK)