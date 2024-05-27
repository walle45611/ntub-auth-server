from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserRegistrationSerializer, UserLoginSerializer


class AuthViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        methods=['post'],
        request_body=UserRegistrationSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='註冊成功',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
                            }
                        )
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: '無效的輸入'
        }
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        logging.info("開始註冊")
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=['post'],
        request_body=UserLoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="登入成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID")
                    }
                )
            ),
            status.HTTP_401_UNAUTHORIZED: '無效的憑證',
            status.HTTP_400_BAD_REQUEST: '無效的輸入'
        }
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        logging.info("開始登入")
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            token_data = serializer.validated_data

            response = Response({
                "access": token_data['access'],
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=['post'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Token刷新成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="新的JWT存取權杖"),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: '無效的輸入',
            status.HTTP_401_UNAUTHORIZED: '無效的權杖'
        }
    )
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        logging.info("正在刷新權杖")
        refresh_token = request.COOKIES.get('refresh_token')
        logging.info(" %s -> 正在刷新權杖", refresh_token)

        if refresh_token is None:
            return Response({"error": "未提供刷新權杖"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            data = {'access': str(token.access_token)}

            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(
                'refresh_token',
                str(token),
                httponly=True,
                max_age=24 * 3600 * 180,
                samesite="Lax",
            )

            return response
        except TokenError as e:
            logging.error(f"權杖無效: {e}")
            return Response({"error": "無效的權杖"}, status=status.HTTP_401_UNAUTHORIZED)
