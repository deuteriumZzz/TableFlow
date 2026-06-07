from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'avatar', 'is_active']
        read_only_fields = ['is_active']

class CustomTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs['refresh']
        data = {
            'refresh': str(refresh),
            'access': str(RefreshToken.for_user(User.objects.get(username=self.context['user'])))
        }
        return data
