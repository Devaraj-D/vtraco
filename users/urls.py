from django.urls import path
from .views import SignupView, LoginView, AddEmployerAPIView,add_employee,ForgotPasswordRequestView,verify_otp, LogoutView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
    path('add-employer/', AddEmployerAPIView.as_view(), name='add-employer'),
    path('add-employee/', add_employee, name='add_employee'),
    path('forgot-password/', ForgotPasswordRequestView.as_view(), name='forgot-password'),
    path('verify_otp/', verify_otp, name='verify_otp'),
]
