from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ParseError
import logging
import requests


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'validators': [validate_password]},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True, 'validators': [validate_email]}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            logging.info(f"Passwords do not match for user {
                         data.get('username')}")
            raise serializers.ValidationError({"password": "密碼和確認密碼不匹配。"})
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此電子郵件已被使用。")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    access_token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            logging.info("email : %s -> 驗證帳號失敗", data['email'])
            raise serializers.ValidationError("驗證帳號失敗")
        refresh = RefreshToken.for_user(user)
        logging.info("email : %s -> 驗證帳號成功", data['email'])
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id
        }


class RefreshTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)


class VerifyGoogleTokenSerializer(serializers.Serializer):
    google_access_token = serializers.CharField(write_only=True, required=True)
    user_id = serializers.IntegerField(read_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, data):
        google_access_token = data['google_access_token']
        google_info_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(google_info_url, params={
                                'access_token': google_access_token})

        if response.status_code != 200:
            logging.error("Google Token 驗證失敗 Response -> %s", response.text)
            raise ParseError("Google Token 驗證失敗")

        user_data = response.json()
        email = user_data.get('email')
        if not email:
            logging.error("Google token does not include an email address")
            raise serializers.ValidationError(
                "Google token must include an email address")

        user, created = User.objects.get_or_create(
            email=email, defaults={'username': email})
        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "user_id": user.id
        }
