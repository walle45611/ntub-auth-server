import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from datetime import datetime, timedelta, timezone
from rest_framework.exceptions import ParseError

class EmailBackend:
    UserModel = get_user_model()

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = self.UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except self.UserModel.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return self.UserModel.objects.get(pk=user_id)
        except self.UserModel.DoesNotExist:
            return None

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(
                token, settings.SIGNING_KEY, algorithms=['HS256'])
            user = get_user_model().objects.get(id=payload['user_id'])
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('invalid token')
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed('user not found')


def create_access_token(data):
    payload = {
        'user_id': data['user_id'],
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SIGNING_KEY, algorithm='HS256')


def create_refresh_token(data):
    payload = {
        'user_id': data['user_id'],
        'exp': datetime.now(timezone.utc) + timedelta(days=30),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SIGNING_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SIGNING_KEY, algorithms='HS256')
        return payload
    except jwt.ExpiredSignatureError:
        raise ParseError("Refresh Token 過期")
    except jwt.InvalidTokenError:
        raise ParseError("非法 Refresh Token")
