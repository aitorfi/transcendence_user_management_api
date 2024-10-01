from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User as DjangoUser
from ..models import User
from ..serializer import UserSerializer
from ..models import ApiUser
from ..serializer import ApiUserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.conf import settings
import os




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
    
