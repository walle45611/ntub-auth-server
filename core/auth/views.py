from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AuthViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        methods=['post'],
        request_body=UserRegistrationSerializer,
        responses={status.HTTP_201_CREATED: openapi.Response('註冊成功', UserRegistrationSerializer),
                   status.HTTP_400_BAD_REQUEST: '無效的輸入'}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "註冊成功", "user": serializer.data}, status=status.HTTP_201_CREATED)
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
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
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
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            token_data = serializer.validated_data

            response = Response({
                "refresh": token_data['refresh'],
                "access": token_data['access'],
                "user_id": token_data['user_id'],
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                'refresh_token',
                token_data['refresh'],
                httponly=True,
                max_age=24 * 3600 * 180,
            )

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
