from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend:
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            users = UserModel.objects.filter(email=email)
            for user in users:
                if user.check_password(password):
                    return user
        except UserModel.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
