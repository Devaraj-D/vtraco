from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from .models import CustomUser
from rest_framework import status
from django.contrib.auth import authenticate


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role_id=validated_data['role_id']
        )
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)

        return {
            'message': 'Signup successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'id_token': {
                'user_id': instance.id,
                'username': instance.username,
                'email': instance.email,
                'role_id': instance.role_id,
            }
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        refresh = RefreshToken.for_user(user)

        # Create a custom ID token (as JWT)
        id_token = AccessToken.for_user(user)
        id_token['email'] = user.email
        id_token['username'] = user.username
        id_token['role_id'] = user.role_id

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
                "id_token": str(id_token)
            }
            }, status=status.HTTP_200_OK)
    

class EmployerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['logo', 'company_name', 'contact', 'designation']

