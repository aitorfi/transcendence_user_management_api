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

def get_default_avatar(request):
    default_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
    if os.path.exists(default_path):
        return FileResponse(open(default_path, 'rb'), content_type="image/jpeg")
    else:
        return HttpResponse("Default avatar not found", status=404)

def get_avatar(request, user_id):
    try:
        api_user = ApiUser.objects.get(user__id=user_id)
        if api_user.avatar_image:
            file_path = api_user.avatar_image.path
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), content_type="image/jpeg")
            else:
                print(f"Avatar file not found: {file_path}")
        else:
            print(f"No avatar_image for user: {user_id}")
    except ApiUser.DoesNotExist:
        print(f"ApiUser not found for user_id: {user_id}")
    except Exception as e:
        print(f"Error retrieving avatar: {str(e)}")
    
    # Si no se encuentra la imagen o el usuario, devolver una imagen por defecto
    default_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
    if os.path.exists(default_path):
        return FileResponse(open(default_path, 'rb'), content_type="image/jpeg")
    else:
        print(f"Default avatar not found at: {default_path}")
        return HttpResponse("Default avatar not found", status=404)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    if 'avatar_image' not in request.FILES:
        return Response({'error': 'No file was submitted'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['avatar_image']
    user = request.user
    api_user = ApiUser.objects.get(user=user)
    
    # Guardar la imagen
    api_user.avatar_image.save(f'img{user.id}.jpg', file, save=True)
    
    return Response({'message': 'Avatar uploaded successfully'}, status=status.HTTP_200_OK)
""" 
def get_avatar(request, user_id):
    try:
        api_user = ApiUser.objects.get(user__id=user_id)
        if api_user.avatar_image:
            return HttpResponse(api_user.avatar_image, content_type="image/jpeg")
    except ApiUser.DoesNotExist:
        pass
    
    # Si no se encuentra la imagen o el usuario, devolver una imagen por defecto
    with open(os.path.join(settings.MEDIA_ROOT, 'default_avatar.jpg'), 'rb') as f:
        return HttpResponse(f.read(), content_type="image/jpeg")

 """