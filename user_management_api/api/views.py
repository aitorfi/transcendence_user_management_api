from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
#este agregamos el modelo de prueba
from .models import User, Prueba
from .serializer import UserSerializer, PruebaSerializer
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse


import os


def serve_index(request):
    # Ruta al archivo index.html
    file_path = os.path.join(settings.BASE_DIR, 'static', 'index.html')
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/html')

@api_view(['GET'])
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

@api_view(['GET'])
def get_pruebas(request):
    pruebas = Prueba.objects.all()
    serializer = PruebaSerializer(pruebas, many=True)
    return Response(serializer.data)
    #return JsonResponse(pruebas, safe=False)

@api_view(['POST'])
def create_prueba(request):
    serializer = PruebaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_prueba_detail(request, pk):
    try:
        prueba = Prueba.objects.get(pk=pk)
    except Prueba.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = PruebaSerializer(prueba)
    return Response(serializer.data)

@api_view(['PUT'])
def update_prueba(request, pk):
    try:
        prueba = Prueba.objects.get(pk=pk)
    except Prueba.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = PruebaSerializer(prueba, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_prueba(request, pk):
    try:
        prueba = Prueba.objects.get(pk=pk)
    except Prueba.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    prueba.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
