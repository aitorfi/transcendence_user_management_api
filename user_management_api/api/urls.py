from django.urls import path
from . import views
from .views import get_users, create_user
from .views import serve_index


urlpatterns = [
	path("users/", get_users, name = "get_users"),
	path("users/create/", create_user, name = "create_user"),
    path('pruebas/', views.get_pruebas, name='get_pruebas'),
    path('pruebas/create/', views.create_prueba, name='create_prueba'),
    path('pruebas/<int:pk>/', views.get_prueba_detail, name='get_prueba_detail'),
    path('pruebas/<int:pk>/update/', views.update_prueba, name='update_prueba'),
    path('pruebas/<int:pk>/delete/', views.delete_prueba, name='delete_prueba'),
    
]
