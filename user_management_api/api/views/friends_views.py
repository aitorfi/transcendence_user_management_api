# Django imports
from django.contrib.auth import authenticate  # Handles user authentication
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.conf import settings  # Access to Django project settings
from django.http import HttpResponse  # Basic HTTP response class

# Rest Framework imports
from rest_framework import status  # Provides HTTP status codes
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework.authentication import TokenAuthentication  # Token-based authentication
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Local imports
from ..models import User, ApiUser  # Custom User and ApiUser models
from ..serializer import UserSerializer, ApiUserSerializer  # Serializers for User and ApiUser models

# Python standard library imports
import os  # Operating system interface, for file and path operations

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_friends(request, pk):
    print(f"Attempting to fetch friends for user ID: {pk}")
    try:
        django_user = DjangoUser.objects.get(id=pk)
        api_user = ApiUser.objects.get(user=django_user)
        
        friends = api_user.friends
        
        if not friends:
            return Response({"friends": []})
        
        # Si friends es una cadena, la dividimos en una lista
        # Asumiendo que los amigos están separados por comas
        friends_list = [friend.strip() for friend in friends.split(',') if friend.strip()]
        
        return Response({"friends": friends_list})
    except DjangoUser.DoesNotExist:
        print(f"No User found for ID: {pk}")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except ApiUser.DoesNotExist:
        print(f"No ApiUser found for User ID: {pk}")
        return Response({"error": "ApiUser not found"}, status=status.HTTP_404_NOT_FOUND)
    
