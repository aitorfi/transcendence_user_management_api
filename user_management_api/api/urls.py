from django.urls import path
from .views import (
    get_users, create_user, get_user,
    login_user, get_user_profile,
    sign_out_user, get_friends,
    update_user_profile,
    change_password
)  


urlpatterns = [
    path("users/", get_users, name="get_users"),
    path("users/<int:pk>/", get_user, name="get_user"),
    path("users/create/", create_user, name="create_user"),
    path('users/login/', login_user, name='login'),
    path('users/signout/', sign_out_user, name='signout'),
    path("users/profile/<int:pk>/", get_user_profile, name="get_user_profile"),
    path("friends/", get_friends, name="get_friends"),
    path("users/update/<int:pk>/", update_user_profile, name="update_user_profile"),
    path("users/change-password/<int:pk>/", change_password, name="change_password"),

]


""" urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/<int:pk>/', views.get_user, name='get_user'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:pk>/', views.update_user, name='update_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
] """