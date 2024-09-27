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
    status = serializers.CharField()
    two_factor_auth = serializers.BooleanField()
    session_42 = serializers.CharField()
    
    class Meta:
        model = ApiUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'age', 'avatar', 'status', 'two_factor_auth', 'session_42']

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
        }
        password = validated_data['password']
        
        django_user = DjangoUser.objects.create_user(**user_data, password=password)
        api_user = ApiUser.objects.create(user=django_user, age=validated_data['age'], avatar=validated_data['avatar'], status=validated_data['status'], two_factor_auth=validated_data['two_factor_auth'], session_42=validated_data['session_42'])
        
        return api_user
		
""" 
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'age': self.age,
            'avatar': self.avatar,
            'status': self.status,
            'two_factor_auth': self.two_factor_auth,
            'session_42': self.session_42

class ApiUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = ApiUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'age']

	def create(self, validated_data):
		user_data = {
			'username': validated_data.pop('username'),
			'email': validated_data.pop('email'),
			'first_name': validated_data.pop('first_name'),
			'last_name': validated_data.pop('last_name'),
		}
		password = validated_data.pop('password', None)
		if not password:
			raise serializers.ValidationError({"password": "This field is required."})

		django_user = DjangoUser.objects.create_user(**user_data, password=password)
		
		age = validated_data.get('age')
		api_user = ApiUser.objects.create(user=django_user, age=age)	
		
		return api_user
 """
"""     def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        password = validated_data.pop('password', None)  # Extrae la contraseña directamente de validated_data
        
        if not password:
            raise serializers.ValidationError({"password": "This field is required."})

        django_user = DjangoUser.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            password=password
        )
        
        api_user = ApiUser.objects.create(user=django_user, **validated_data)
        return api_user 
		"""