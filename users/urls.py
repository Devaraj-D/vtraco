from django.urls import path
from .views import SignupView, LoginView, AddEmployerAPIView,add_employee

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView, name='login'),
    path('add-employer/', AddEmployerAPIView.as_view(), name='add-employer'),
    path('add-employee/', add_employee, name='add_employee'),
]
