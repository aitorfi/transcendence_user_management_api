# Django imports
from django.contrib.auth import authenticate  # Handles user authentication
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.contrib.auth.decorators import login_required  # Decorator to restrict access to logged-in users
from django.conf import settings  # Access to Django project settings
from django.http import HttpResponse, JsonResponse  # HTTP response classes

# Django Rest Framework imports
from rest_framework import status  # Provides HTTP status codes
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework.authentication import TokenAuthentication  # Token-based authentication
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Simple JWT imports
from rest_framework_simplejwt.tokens import RefreshToken  # Handles refresh tokens for JWT
from rest_framework_simplejwt.authentication import JWTAuthentication  # JWT authentication backend

# Third-party library imports
import pyotp  # Implements TOTP (Time-based One-Time Password) algorithm for 2FA

# Python standard library imports
import os  # Operating system interface, for file and path operations
import logging  # Logging facility for Python

# Local imports
from ..models import User, ApiUser  # Custom User and ApiUser models
from ..serializer import UserSerializer, ApiUserSerializer  # Serializers for User and ApiUser models


logger = logging.getLogger(__name__)  # Creates a logger instance for this module
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)  # Configures basic logging to a file


# Python standard library imports
import os  # Operating system interface, for file and path operations






from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def friends_blocked(request, friend_id):
    logger.debug(f"add_friend_to_friends_blocked called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        # Obtener el ApiUser correspondiente al usuario autenticado
        api_user = ApiUser.objects.get(user=request.user)

        # Si no existe la lista de friends_blocked, crearla
        if not api_user.friends_blocked:
            friends_blocked_ids = []
        else:
            # Convertir la lista de friends_blocked en una lista de enteros
            friends_blocked_ids = [int(id) for id in api_user.friends_blocked.split(',') if id.strip().isdigit()]

        # Si el friend_id ya está en la lista de friends_blocked, devolver un error
        if friend_id in friends_blocked_ids:
            return Response({"error": "This user is already in your blocked list"}, status=400)

        # Agregar el nuevo friend_id a la lista
        friends_blocked_ids.append(friend_id)

        # Actualizar el campo friends_blocked en el modelo con la nueva lista
        api_user.friends_blocked = ','.join(map(str, friends_blocked_ids))
        api_user.save()

        return Response({"message": "Friend successfully blocked"})

    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in add_friend_to_friends_blocked: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)
  


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_from_friendswaiting(request, friend_id):
    logger.debug(f"remove_from_friendswaiting called for user: {request.user.username}, friend_id: {friend_id}")

    try:
        # Aseguramos que friend_id sea un entero válido
        friend_id = int(friend_id)

        # Obtenemos el ApiUser del "usuario amigo"
        friend_user = ApiUser.objects.filter(user_id=friend_id).first()
        if not friend_user:
            return Response({"error": "Friend not found"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener el ApiUser del usuario autenticado
        api_user = ApiUser.objects.filter(user=request.user).first()
        if not api_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Verificamos si el usuario que hace la petición está en la lista friends_wait del amigo
        friends_waiting = friend_user.friends_wait or ""
        friends_waiting_ids = [int(id) for id in friends_waiting.split(',') if id.strip().isdigit()]
        logger.debug(f"Friend's current waiting requests: {friends_waiting_ids}")

        if api_user.user.id not in friends_waiting_ids:
            return Response({"error": "You are not in this user's waiting list"}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar al usuario de la lista friends_waiting
        friends_waiting_ids.remove(api_user.user.id)
        friend_user.friends_wait = ','.join(map(str, friends_waiting_ids)) if friends_waiting_ids else ""
        friend_user.save()

        return Response({"message": "You have been successfully removed from the friend's waiting list"}, status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "Invalid friend_id format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_from_friendswaiting: {str(e)}")
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_request(request, friend_id):
    logger.debug(f"remove_request called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends_request:
            return Response({"error": "You have no friend requests to remove"}, status=400)
        
        # Convertimos friend_id a entero
        friend_id = int(friend_id)
        
        friends_ids = [int(id) for id in api_user.friends_request.split(',') if id.strip().isdigit()]
        logger.debug(f"Current friend requests: {friends_ids}")
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friend requests"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends_request = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend request removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_request: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_wait(request, friend_id):
    logger.debug(f"remove_friend waiting called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends_wait:
            return Response({"error": "You have no friends waiting to remove"}, status=400)
        
        friends_ids = [int(id) for id in api_user.friends_wait.split(',') if id.strip().isdigit()]
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends_wait = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend wait removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friends_request(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        # Obtener el usuario amigo (el receptor de la solicitud)
        friend_user = DjangoUser.objects.get(id=friend_id) #iker   id  AMIGO
        friend_api_user = ApiUser.objects.get(user=friend_user) #iker username    
        
        # Obtener el usuario que envía la solicitud (usuario autenticado)
        api_user = ApiUser.objects.get(user=request.user)
        
        # Actualizar el campo 'friends_request' del amigo para que contenga el ID del usuario autenticado
        if not friend_api_user.friends_request:
            # Si el campo está vacío, asigna directamente el ID del usuario autenticado
            friend_api_user.friends_request = str(api_user.user.id)  # El usuario autenticado que envía la solicitud
        else:
            # Si ya existen solicitudes, agrega el ID del usuario autenticado si no está presente
            friends_request_list = friend_api_user.friends_request.split(',')
            if str(api_user.user.id) not in friends_request_list:
                friends_request_list.append(str(api_user.user.id))  # Añadir el ID del usuario autenticado
                friend_api_user.friends_request = ','.join(friends_request_list)
            else:
                return Response({"message": "Friend request already sent to this user"}, status=200)
        
        # Guardar los cambios en el usuario amigo
        friend_api_user.save()
        return Response({"message": "Friend request sent successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "Friend user not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser for friend not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friends_wait(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        friends_wait = DjangoUser.objects.get(id=friend_id)
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends_wait:
            api_user.friends_wait = str(friend_id)
        else:
            friends_wait_list = api_user.friends_wait.split(',')
            if str(friend_id) not in friends_wait_list:
                friends_wait_list.append(str(friend_id))
                api_user.friends_wait = ','.join(friends_wait_list)
            else:
                return Response({"message": "User is already in friends_wait list"}, status=200)
        
        api_user.save()
        return Response({"message": "Friend added to wait list successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friend(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        friend = DjangoUser.objects.get(id=friend_id)
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            api_user.friends = str(friend_id)
        else:
            friends_list = api_user.friends.split(',')
            if str(friend_id) not in friends_list:
                friends_list.append(str(friend_id))
                api_user.friends = ','.join(friends_list)
            else:
                return Response({"message": "User is already a friend"}, status=200)
        
        api_user.save()
        return Response({"message": "Friend added successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

#########################
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friend_final(request):
    friend_id = request.data.get('friend_id')
    
    # Verificar si se proporciona el ID del amigo
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        # Buscar el amigo por su ID en DjangoUser
        friend = DjangoUser.objects.get(id=friend_id)
        # Buscar el usuario que realiza la solicitud
        api_user = ApiUser.objects.get(user=request.user)
        # Buscar el usuario amigo en ApiUser
        friend_api_user = ApiUser.objects.get(user=friend)

        # Agregar el amigo a la lista del usuario que realiza la solicitud
        if not api_user.friends:
            api_user.friends = str(friend_id)
        else:
            friends_list = api_user.friends.split(',')
            if str(friend_id) not in friends_list:
                friends_list.append(str(friend_id))
                api_user.friends = ','.join(friends_list)
            else:
                return Response({"message": "User is already a friend"}, status=200)

        # Agregar el usuario que hizo la solicitud a la lista de amigos del amigo
        if not friend_api_user.friends:
            friend_api_user.friends = str(api_user.user.id)
        else:
            friend_friends_list = friend_api_user.friends.split(',')
            if str(api_user.user.id) not in friend_friends_list:
                friend_friends_list.append(str(api_user.user.id))
                friend_api_user.friends = ','.join(friend_friends_list)
            else:
                return Response({"message": "You are already in their friend list"}, status=200)
        
        # Guardar los cambios para ambos usuarios
        api_user.save()
        friend_api_user.save()

        return Response({"message": "Friend added successfully"}, status=201)

    except DjangoUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_blocked(request, friend_id):
    logger.debug(f"remove_friend called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            return Response({"error": "You have no friends blocked to remove"}, status=400)
        
        friends_ids = [int(id) for id in api_user.friends_blocked.split(',') if id.strip().isdigit()]
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends_blocked = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend blocked removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend(request, friend_id):
    logger.debug(f"remove_friend called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        # Obtener el perfil del usuario autenticado
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            return Response({"error": "You have no friends to remove"}, status=400)
        
        # Convertir la lista de amigos del usuario autenticado a una lista de enteros
        friends_ids = [int(id) for id in api_user.friends.split(',') if id.strip().isdigit()]
        
        # Verificar si el friend_id está en la lista de amigos
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        # Eliminar el friend_id de la lista de amigos del usuario autenticado
        friends_ids.remove(friend_id)
        api_user.friends = ','.join(map(str, friends_ids))
        api_user.save()

        # Intentar obtener el perfil del usuario asociado al friend_id
        try:
            friend_user = ApiUser.objects.get(user__id=friend_id)
            
            # Convertir la lista de amigos del friend_id a una lista de enteros
            friend_user_friends_ids = [int(id) for id in friend_user.friends.split(',') if id.strip().isdigit()]
            
            # Verificar si el usuario autenticado está en la lista de amigos del friend_id
            if request.user.id in friend_user_friends_ids:
                # Eliminar el usuario autenticado de la lista de amigos del friend_id
                friend_user_friends_ids.remove(request.user.id)
                friend_user.friends = ','.join(map(str, friend_user_friends_ids))
                friend_user.save()
            
        except ApiUser.DoesNotExist:
            logger.warning(f"User with id {friend_id} not found, skipping removal from their friend list")

        return Response({"message": "Friend removed successfully from both lists"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_request(request):
    logger.debug(f"get_friends_request called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_request:
            logger.debug("User has no friends request")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_request string: {api_user.friends_request}")
        friends_request_ids = [int(friend_id) for friend_id in api_user.friends_request.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_request IDs: {friends_request_ids}")
        
        friends_request = DjangoUser.objects.filter(id__in=friends_request_ids).values('id', 'username')
        logger.debug(f"Found friends request: {list(friends_request)}")
        
        return Response({"friends": list(friends_request)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_blocked(request):
    logger.debug(f"get_friends_blocked called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_blocked:
            logger.debug("User has no friends blocked")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_blocked string: {api_user.friends_blocked}")
        friends_blocked_ids = [int(friend_id) for friend_id in api_user.friends_blocked.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_blocked IDs: {friends_blocked_ids}")
        
        friends_blocked = DjangoUser.objects.filter(id__in=friends_blocked_ids).values('id', 'username')
        logger.debug(f"Found friends blocked: {list(friends_blocked)}")
        
        return Response({"friends": list(friends_blocked)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_wait(request):
    logger.debug(f"get_friends_wait called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_wait:
            logger.debug("User has no friends waiting")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_wait string: {api_user.friends_wait}")
        friends_wait_ids = [int(friend_id) for friend_id in api_user.friends_wait.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_wait IDs: {friends_wait_ids}")
        
        friends_wait = DjangoUser.objects.filter(id__in=friends_wait_ids).values('id', 'username')
        logger.debug(f"Found friends waiting: {list(friends_wait)}")
        
        return Response({"friends": list(friends_wait)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
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
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_friends(request):
    logger.debug(f"get_user_friends called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends:
            logger.debug("User has no friends")
            return Response({"friends": []})
        
        logger.debug(f"User's friends string: {api_user.friends}")
        friends_ids = [int(friend_id) for friend_id in api_user.friends.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend IDs: {friends_ids}")
        
        friends = DjangoUser.objects.filter(id__in=friends_ids).values('id', 'username')
        logger.debug(f"Found friends: {list(friends)}")
        
        return Response({"friends": list(friends)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_user_friends: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

