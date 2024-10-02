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
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os


def logout(request):
    # Revoca el token de 42
    token = request.auth.key
    response = requests.post('https://api.intra.42.fr/oauth/token/info', headers={
        'Authorization': f'Bearer {token}'
    })
    
    if response.status_code == 200:
        # El token es válido, procede a revocarlo
        revoke_response = requests.post('https://api.intra.42.fr/oauth/token/revoke', data={
            'client_id': settings.FORTYTWO_CLIENT_ID,
            'client_secret': settings.FORTYTWO_CLIENT_SECRET,
            'token': token
        })
        
        if revoke_response.status_code == 200:
            # Token revocado exitosamente
            # Aquí puedes eliminar el token de tu base de datos si lo almacenas
            request.auth.delete()
            return Response({"message": "Logged out successfully"})
        else:
            return Response({"error": "Failed to revoke token"}, status=400)
    else:
        # El token ya no es válido, simplemente elimínalo de tu sistema
        request.auth.delete()
        return Response({"message": "Logged out successfully"})

@login_required
def check_auth(request):
    return JsonResponse({
        'authenticated': True,
        'username': request.user.username,
        'token': request.session.get('oauth_token')
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "Tienes acceso a esta vista protegida"})

def home(request):
    if request.user.is_authenticated:
        return HttpResponse(f"Bienvenido, {request.user.username}! <a href='/oauth/logout/'>Cerrar sesión</a> | <a href='/protected/'>Vista protegida</a>")
    else:
        return HttpResponse("Bienvenido, visitante! <a href='/oauth/login/'>Iniciar sesión con 42</a>")

def get_auth_url(request):
    auth_url = f"{settings.OAUTH2_AUTH_URL}?client_id={settings.OAUTH2_CLIENT_ID}&redirect_uri={settings.OAUTH2_REDIRECT_URI}&response_type=code"
    return JsonResponse({"auth_url": auth_url})

def oauth_login(request):
    auth_url = f"{settings.OAUTH2_AUTH_URL}?client_id={settings.OAUTH2_CLIENT_ID}&redirect_uri={settings.OAUTH2_REDIRECT_URI}&response_type=code"
    return redirect(auth_url)


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

