from rest_framework import serializers
from django.contrib.auth.models import User as DjangoUser
from .models import ApiUser, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ApiUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    friends = serializers.CharField(allow_blank=True, required=False)
    friends_wait = serializers.CharField(allow_blank=True, required=False)
    friends_request = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ApiUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'friends', 'friends_wait', 'friends_request'
        ]

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
        }
        password = validated_data['password']
        
        django_user = DjangoUser.objects.create_user(**user_data, password=password)
        api_user = ApiUser.objects.create(
            user=django_user,
            friends=validated_data.get('friends', ''),
            friends_wait=validated_data.get('friends_wait', ''),
            friends_request=validated_data.get('friends_request', ''),
        )
        
        return api_user