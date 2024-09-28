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
from django.conf import settings
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session
from rest_framework.decorators import api_view, authentication_classes, permission_classes
#from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
#from two_factor.utils import default_device
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
#from two_factor.utils import default_device
from django.shortcuts import redirect
#from django_otp.plugins.otp_totp.models import TOTPDevice
#import qrcode
#import qrcode.image.svg
from io import BytesIO
import base64

""" @api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    user = request.user
    device, created = TOTPDevice.objects.get_or_create(user=user, name="default")
    
    if created:
        device.save()

    # Genera la URL para Google Authenticator
    totp_url = device.config_url

    # Genera el código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convierte la imagen a base64 para enviarla al frontend
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return Response({
        'qr_code': img_str,
        'secret_key': device.key,
    }) """

""" @api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        if hasattr(user, 'apiuser') and user.apiuser.two_factor_auth:
            if default_device(user):
                # El usuario tiene 2FA activado y configurado
                # Aquí deberías manejar la verificación del código 2FA
                otp_token = request.data.get('otp_token')
                if otp_token and user.verify_otp(otp_token):
                    login(request, user)
                    # Genera y devuelve el token de autenticación
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user_id': user.pk,
                        'username': user.username
                    })
                else:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # El usuario tiene 2FA activado pero no configurado
                return Response({'error': '2FA not set up'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # El usuario no tiene 2FA activado
            login(request, user)
            # Genera y devuelve el token de autenticación
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
 """
""" @api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    # Tu lógica aquí
    return Response({"message": "Esta es una vista protegida"})

def oauth42_login(request):
    print("OAuth42 login view called")
    oauth = OAuth2Session(settings.OAUTH42_CLIENT_ID, redirect_uri=settings.OAUTH42_REDIRECT_URI)
    authorization_url, state = oauth.authorization_url('https://api.intra.42.fr/oauth/authorize')
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def oauth42_callback(request):
    oauth = OAuth2Session(settings.OAUTH42_CLIENT_ID, state=request.session['oauth_state'])
    token = oauth.fetch_token('https://api.intra.42.fr/oauth/token',
                              client_secret=settings.OAUTH42_CLIENT_SECRET,
                              authorization_response=request.build_absolute_uri())
    user_info = oauth.get('https://api.intra.42.fr/v2/me').json()
    # Aquí procesas la información del usuario y lo autenticas en tu sistema
    # Por ejemplo, podrías crear un usuario si no existe, o iniciar sesión si ya existe
    # Luego, redirige al usuario a la página principal o al perfil
    return redirect('http://localhost:5500/Profile')  # Ajusta esta URL según tu frontend
 """

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