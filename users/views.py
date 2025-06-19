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
from .utils import send_invitation_email
from django.core.mail import send_mail
import random
import string


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