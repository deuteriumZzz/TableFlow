from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from apps.accounts.models import User

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        user = authenticate(username=username, password=password)
        if user:
            user.last_login_pos = timezone.now()
            user.save()
        return user

    @staticmethod
    def create_user(data):
        user = User(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'cashier'),
        )
        user.save()
        return user
