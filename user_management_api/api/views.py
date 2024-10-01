from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User as DjangoUser
from .models import User
from .serializer import UserSerializer
from .models import ApiUser
from .serializer import ApiUserSerializer
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
    


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request, pk):
    user = request.user
    
    if user.id != pk:
        return Response({"error": "You don't have permission to change this user's password"}, 
                        status=status.HTTP_403_FORBIDDEN)

    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({"error": "Both current and new password are required"}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # Verificar la contraseña actual
    if not authenticate(username=user.username, password=current_password):
        return Response({"error": "Current password is incorrect"}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # Cambiar la contraseña
    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request, pk):
    try:
        django_user = DjangoUser.objects.get(id=pk)
        api_user = ApiUser.objects.get(user=django_user)
    except (DjangoUser.DoesNotExist, ApiUser.DoesNotExist):
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Actualizar los campos del usuario Django
    django_user.first_name = request.data.get('first_name', django_user.first_name)
    django_user.last_name = request.data.get('last_name', django_user.last_name)
    django_user.save()

    # Actualizar los campos del ApiUser
    api_user.friends = request.data.get('friends', api_user.friends)
    api_user.save()

    # Devolver los datos actualizados
    return Response(api_user.get_full_user_data(), status=status.HTTP_200_OK)






@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request, pk):
    print(f"Attempting to fetch profile for user ID: {pk}")
    try:
        django_user = DjangoUser.objects.get(id=pk)
        api_user, created = ApiUser.objects.get_or_create(user=django_user)
        if created:
            print(f"ApiUser created for user ID: {pk}")
        print(f"ApiUser found: {api_user}")
        return Response(api_user.get_full_user_data())
    except DjangoUser.DoesNotExist:
        print(f"No User found for ID: {pk}")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)






@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


""" @api_view(['GET'])
def get_users(request):
	user = User.objects.all()
	serializer = UserSerializer(user, many = True)
	return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
	serializer = UserSerializer(data = request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status = status.HTTP_201_CREATED)
	return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
 """

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sign_out_user(request):
    try:
        # Obtener el token del usuario actual
        token = request.auth

        if token:
            # Eliminar el token
            token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No active session found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_user(request, pk):
    try:
        api_user = ApiUser.objects.get(user__id=pk)
        return Response(api_user.get_full_user_data())
    except ApiUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_users(request):
    api_users = ApiUser.objects.all()
    user_data = [api_user.get_full_user_data() for api_user in api_users]
    return Response(user_data)


""" @api_view(['GET'])
def get_user(request, pk):
    try:
        user = ApiUser.objects.get(pk=pk)
        full_data = user.get_full_user_data()
        return Response(full_data)
    except ApiUser.DoesNotExist:
        return  Response(status=status.HTTP_404_NOT_FOUND)
"""


@api_view(['POST'])
def create_user(request):
    serializer = ApiUserSerializer(data=request.data)
    if serializer.is_valid():
        api_user = serializer.save()
        return Response(api_user.get_full_user_data(), status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

""" 
@api_view(['PUT'])
def update_user(request, pk):
    try:
        user = ApiUser.objects.get(pk=pk)
    except ApiUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ApiUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_user(request, pk):
    try:
        user = ApiUser.objects.get(pk=pk)
    except ApiUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT) 
"""