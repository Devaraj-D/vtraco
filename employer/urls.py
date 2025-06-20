from django.urls import path
from . import views
from .views import get_all_employees
from .views import bulk_update_salary

urlpatterns = [
    path('employees/', views.list_employees, name='list_employees'),
    path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('salary/<int:id>/', views.update_salary, name='update_salary'),
    path('get-all-employees/', get_all_employees, name='get-all-employees'),
    path('bulk-update-salary', views.bulk_update_salary, name='bulk-update-salary'),
]
