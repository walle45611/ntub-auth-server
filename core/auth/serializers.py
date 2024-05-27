from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import logging


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            logging.info("{data} 密碼和確認密碼不匹配")
            raise serializers.ValidationError({"password": "密碼和確認密碼不匹配。"})
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            logging.info("email : %s, password: %s -> 驗證帳號失敗",
                         data['email'], data['password'])
            raise serializers.ValidationError("驗證帳號失敗")
        refresh = RefreshToken.for_user(user)
        logging.info("email : %s, password: %s -> 驗證帳號成功",
                     data['email'], data['password'])
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id
        }
