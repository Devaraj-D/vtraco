from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
import re
from .serializers import EmployerUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from .utils import send_invitation_email,send_otp_email
from django.core.mail import send_mail
import random
import string
from django.conf import settings
from .models import OTPVerification,CustomUser
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken, TokenError



User = get_user_model()


# Email regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Password: at least 8 chars, one letter, one number, one special char
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'


class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        role_id = request.data.get("role_id")

        if not all([username, email, password, role_id]):
            return Response({
                "status": "error",
                "message": "All fields (username, email, password, role_id) are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email
        if not re.match(EMAIL_REGEX, email):
            return Response({
                "status": "error",
                "message": "Invalid email format."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password
        if not re.match(PASSWORD_REGEX, password):
            return Response({
                "status": "error",
                "message": "Password must be at least 8 characters long, include at least one letter, one number, and one special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "status": "error",
                "message": "User with this email already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role_id=role_id
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # ID token
        id_token_payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role_id': user.role_id,
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'iat': datetime.utcnow()
        }
        id_token = jwt.encode(id_token_payload, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            "status": "success",
            "message": "Signup successful",
            "user": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role_id": user.role_id
            },
            "tokens": {
                "access": access_token,
                "refresh": str(refresh),
                "id_token": id_token
            }
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def LoginView(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password required"}, status=400)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Login successful",
            "user": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role_id": user.role_id
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id_token": str(refresh.access_token)  # you can replace this if you want a separate id_token
            }
        })
    else:
        return Response({"error": "Invalid email or password"}, status=401)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    try:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            "status": "success",
            "message": "Logout successful. Token blacklisted."
        }, status=status.HTTP_205_RESET_CONTENT)

    except TokenError:
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        

class AddEmployerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        
        if user.role_id != 2:
            return Response({"detail": "Only Employers can update employer profile."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = EmployerUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Employer profile updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
User = get_user_model()

def generate_password():
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(chars) for _ in range(8))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password)):
            return password
       
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_employee(request):
    employer = request.user

    if employer.role_id != 2:
        return Response({"detail": "Only employers can add employees."}, status=status.HTTP_403_FORBIDDEN)

    try:
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"error": "Employee with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        password = generate_password()

        employee = User.objects.create_user(
            username=request.data.get('email'),
            employee_name=request.data.get('employee_name'),
            email=email,
            password=password,
            role_id=3,  # role_id = 3 for Employee
            company_name=request.data.get('company_name'),
            contact=request.data.get('phone'),
            designation=request.data.get('designation'),
            dob=request.data.get('dob'),
            salary=request.data.get('salary'),
            joining_date=request.data.get('joining_date')
        )

        # Send invitation email using SendGrid
        send_invitation_email(email=email, username=email, password=password)

        return Response({
            "status": "success",
            "message": "Employee created and invitation sent successfully.",
            "employee_id": employee.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordRequestView(APIView):
    authentication_classes = []  # Disable JWT for this public endpoint
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "No user with this email"}, status=status.HTTP_404_NOT_FOUND)

        otp_code = str(random.randint(1000, 9999))

        OTPVerification.objects.update_or_create(
            user=user,
            defaults={"otp": otp_code, "created_at": timezone.now()}
        )

        send_otp_email(email=user.email, username=user.username, otp=otp_code)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

    if not all([email, otp, new_password]):
        return Response({"error": "Email, OTP, and new_password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
        otp_entry = OTPVerification.objects.get(user=user, otp=otp)

        # Check if OTP is expired (e.g., valid for 10 mins)
        if timezone.now() - otp_entry.created_at > timedelta(minutes=10):
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password securely
        user.set_password(new_password)
        user.save()

        # Optionally delete the used OTP
        otp_entry.delete()

        return Response({
            "status": "success",
            "message": "Password reset successfully."
        }, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except OTPVerification.DoesNotExist:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
