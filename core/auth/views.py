from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ParseError, NotAuthenticated
from drf_spectacular.utils import extend_schema
import logging

from .serializers import UserRegistrationSerializer, UserLoginSerializer, VerifyGoogleTokenSerializer, RefreshTokenSerializer


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            200: UserRegistrationSerializer
        },
        description="註冊使用者並回傳使用者資料。"
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        logging.info("開始註冊")
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"user": serializer.data}, 200)
        logging.error("註冊失敗 Error -> %s", str(serializer.errors))
        raise ParseError("註冊失敗")

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: UserLoginSerializer,
        },
        description="登入後回傳 Access Token 和 Refresh Token。"
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        logging.info("開始登入")
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            token_data = serializer.validated_data

            response = Response({
                "access_token": token_data['access'],
                "user_id": token_data['user_id'],
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                'refresh_token',
                token_data['refresh'],
                httponly=True,
                max_age=24 * 3600 * 180,
                samesite="Lax",
            )
            return response
        logging.warning("登入失敗 Error -> %s", str(serializer.errors))
        raise ParseError("登入失敗")

    @extend_schema(
        responses={
            200: RefreshTokenSerializer,
        },
        description="更新 Access Token。"
    )
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        logging.info("正在刷新權杖")
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            logging.warning("請重新登入")
            raise ParseError('沒有提供 Refresh Token')
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            response = Response({'access_token': str(new_access_token)})
            return response
        except TokenError as e:
            logging.error("非法登入 Error -> %s", str(e))
            raise NotAuthenticated("非法登入")

    @extend_schema(
        request=VerifyGoogleTokenSerializer,
        responses={
            200: VerifyGoogleTokenSerializer,
        },
        description="驗證 Google 登入的 Token 並回傳新的 Access Token 和 Refresh Token。"
    )
    @action(methods=['post'], detail=False, url_path='verify-google-token')
    def verify_google_token(self, request):
        logging.info("開始 Google 登入")
        serializer = VerifyGoogleTokenSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            response = Response({
                'access_token': validated_data['access_token'],
                'user_id': validated_data['user_id']
            }, status=200)

            response.set_cookie(
                'refresh_token',
                validated_data['refresh_token'],
                httponly=True,
                max_age=24 * 3600 * 180,
                samesite='Lax'
            )

            logging.info("使用者 %s 透過 Google 登入成功", validated_data['user_id'])
            return response
        logging.error("Google 登入失敗 Error -> %s", str(serializer.errors))
        raise ParseError("Google 登入失敗")
