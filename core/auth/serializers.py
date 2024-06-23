from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
import logging
import requests

from .authentication import create_access_token, create_refresh_token, decode_token


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'validators': [validate_password]},
            'password2': {'write_only': True, 'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        validate_password(data['password'], self.instance)
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
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
            logging.info("email : %s, password: %s -> 驗證帳號失敗",
                         data['email'], data['password'])
            raise serializers.ValidationError("驗證帳號失敗")

        token_payload = {'user_id': data['email']}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        logging.info("email : %s, password: %s -> 驗證帳號成功",
                     data['email'], data['password'])
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, data):
        refresh_token = data.get('refresh_token')
        user_data = decode_token(refresh_token)
        new_access_token = create_access_token(
            {'user_id': user_data['user_id']}
        )
        return {
            'access_token': new_access_token
        }


class VerifyGoogleTokenSerializer(serializers.Serializer):
    google_access_token = serializers.CharField(write_only=True, required=True)
    user_id = serializers.IntegerField(read_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, data):
        google_info_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(google_info_url, params={
                                'access_token': data['google_access_token']})

        if response.status_code != 200:
            raise serializers.ValidationError(
                "Google Token verification failed")

        user_data = response.json()
        email = user_data.get('email')
        if not email:
            raise serializers.ValidationError(
                "Google token must include an email address")

        token_payload = {'user_id': email}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
