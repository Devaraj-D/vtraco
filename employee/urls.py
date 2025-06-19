from django.urls import path
from .views import attendance_login, attendance_logout, get_employees, employee_request, get_employee_salary_details, update_profile_info, update_employee_request,get_user_notifications

urlpatterns = [
    path('attendance/login/', attendance_login, name='attendance_login'),
    path('attendance/logout/', attendance_logout, name='attendance_logout'),
    path('get_employees/', get_employees, name='get_employees'),
    path('employee-request/', employee_request, name='employee_request'),
    path('employee_salary/', get_employee_salary_details, name='get_employee_salary_details'),
    path('update-profile/', update_profile_info, name='update-profile'),
    path('update_employee_request/<int:request_id>/', update_employee_request, name='update_employee_request'),
    path('notifications/', get_user_notifications, name='get-user-notifications'),
]
