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
    age = serializers.IntegerField()
    avatar = serializers.CharField()
    friends = serializers.CharField(allow_blank=True, required=False)
    friends_wait = serializers.CharField(allow_blank=True, required=False)
    friends_request = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField()
    two_factor_auth = serializers.BooleanField()
    session_42 = serializers.CharField()
    
    class Meta:
        model = ApiUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'age', 'avatar', 'friends', 'friends_wait', 'friends_request',
            'status', 'two_factor_auth', 'session_42'
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
            user=django_user, age=validated_data['age'], avatar=validated_data['avatar'], friends=validated_data['friends'], 
            friends_wait=validated_data['friends_wait'],  friends_request=validated_data['friends_request'], status=validated_data['status'], 
            two_factor_auth=validated_data['two_factor_auth'], session_42=validated_data['session_42'])
        
        return api_user
	