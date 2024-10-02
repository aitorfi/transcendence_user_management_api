from django.http import JsonResponse, HttpResponse  # Añadimos HttpResponse aquí
from django.conf import settings
from requests_oauthlib import OAuth2Session
import logging
from django.contrib.auth import logout
import json


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
        print("Token obtenido:", token)  # Esto imprimirá el token en la consola del servidor
        request.session['oauth_token'] = token
        user_info = get_user_info(request)
        print("Información del usuario:", user_info)
        
        # Aquí deberías crear o actualizar el usuario en tu base de datos
        # y realizar el login del usuario en tu sistema

        # Crea una respuesta JSON con la información que quieres pasar al frontend
        response_data = {
            'status': 'success',
            'message': 'Autenticación exitosa',
            'user': user_info
        }
        
        # Crea una respuesta con la URL de redirección y los datos
        response = JsonResponse(response_data)
        response['Location'] = settings.LOGIN_REDIRECT_URL
        response.status_code = 302  # Código de redirección
        
        return response
    except Exception as e:
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

def auth_logout(request):
    logout(request)
    return HttpResponse("Has cerrado sesión exitosamente.")

def create_or_update_user(user_info):
    username = user_info['login']
    email = user_info['email']
    
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.first_name = user_info.get('first_name', '')
    user.last_name = user_info.get('last_name', '')
    user.save()

    api_user, _ = ApiUser.objects.get_or_create(user=user)
    # Aquí puedes actualizar campos adicionales de ApiUser si es necesario
    
    return user