from rest_framework import serializers
from .models import User
# aqui tenemos que agrgar el modelo de prueba
from .models import Prueba

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'

class PruebaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prueba
        fields = ['id', 'username', 'email', 'avatar', 'status', 'created_at', 'updated_at', 'two_factor_auth']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Aquí puedes agregar lógica personalizada para la creación
        # Por ejemplo, cifrar la contraseña antes de guardarla
        return Prueba.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Aquí puedes agregar lógica personalizada para la actualización
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance