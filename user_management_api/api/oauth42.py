from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from requests_oauthlib import OAuth2Session
from django.contrib.auth import login, logout
from django.contrib.auth.models import User as DjangoUser
from .models import ApiUser
from rest_framework.authtoken.models import Token
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from oauth2_provider.models import AccessToken
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login



User = get_user_model()
logger = logging.getLogger(__name__)

def get_oauth_session(state=None):
    return OAuth2Session(
        settings.OAUTH2_CLIENT_ID,
        redirect_uri=settings.OAUTH2_REDIRECT_URI,
        state=state
    )

def auth_login(request):
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(settings.OAUTH2_AUTH_URL)
    request.session['oauth_state'] = state
    logger.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)


def auth_callback(request):
    oauth = get_oauth_session(state=request.session.get('oauth_state'))
    try:
        token = oauth.fetch_token(
            settings.OAUTH2_TOKEN_URL,
            client_secret=settings.OAUTH2_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri()
        )
        logger.debug(f"Token obtenido: {token}")
        request.session['oauth_token'] = token
        user_info = get_user_info(request)
        logger.debug(f"Información del usuario: {user_info}")
        
        if user_info:
            user = create_or_update_user(user_info)
            logger.debug(f"Usuario creado/actualizado: {user.username}")
            
            # Crear o actualizar el token de acceso
            expires = timezone.now() + timedelta(seconds=token['expires_in'])
            access_token, _ = AccessToken.objects.update_or_create(
                user=user,
                defaults={
                    'token': token['access_token'],
                    'expires': expires,
                    'scope': token.get('scope', '')
                }
            )
            
            # Iniciar sesión del usuario especificando el backend
            login(request, user, backend='oauth2_provider.backends.OAuth2Backend')

            response_data = {
                'status': 'success',
                'message': 'Autenticación exitosa',
                'user': user.apiuser.get_full_user_data(),
                'access_token': access_token.token,
                'redirect_url': settings.LOGIN_REDIRECT_URL
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'No se pudo obtener la información del usuario'}, status=400)
    except Exception as e:
        logger.exception(f"Error en auth_callback: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

def get_user_info(request):
    token = request.session.get('oauth_token')
    if not token:
        logger.error("No token found in session")
        return None
    oauth = OAuth2Session(settings.OAUTH2_CLIENT_ID, token=token)
    try:
        user_info = oauth.get(settings.OAUTH2_API_BASE_URL + 'me').json()
        return user_info
    except Exception as e:
        logger.exception(f"Error fetching user info: {str(e)}")
        return None

def create_or_update_user(user_info):
    oauth_id = str(user_info['id'])
    email = user_info.get('email', '')
    username = user_info['login']
    
    try:
        api_user = ApiUser.objects.get(oauth_id=oauth_id)
        user = api_user.user
        logger.debug(f"Usuario existente encontrado: {user.username}")
    except ApiUser.DoesNotExist:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.email = email
            user.set_unusable_password()
            user.is_active = True
            user.save()
            logger.debug(f"Nuevo usuario creado: {user.username}")
        api_user = ApiUser.objects.create(user=user, oauth_id=oauth_id, user_42=True)
        logger.debug(f"Nuevo ApiUser creado para: {user.username}")
    
    # Actualizar información del usuario
    user.email = email
    user.first_name = user_info.get('first_name', '')
    user.last_name = user_info.get('last_name', '')
    user.is_active = True
    user.save()

    api_user.user_42 = True
    api_user.save()
    
    logger.debug(f"Usuario actualizado: {user.username}")
    return user


def auth_logout(request):
    logout(request)
    return JsonResponse({"message": "Has cerrado sesión exitosamente."})