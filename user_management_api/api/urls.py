
from django.urls import path
from .views import user_views, avatar_views, friends_views

urlpatterns = [
    path("users/", user_views.get_users, name="get_users"),
    path("users/<int:pk>/", user_views.get_user, name="get_user"),
    path("users/create/", user_views.create_user, name="create_user"),
    path('users/login/', user_views.login_user, name='login'),
    path('users/signout/', user_views.sign_out_user, name='signout'),
    path("users/profile/<int:pk>/", user_views.get_user_profile, name="get_user_profile"),
    path("friends/", friends_views.get_friends, name="get_friends"),
    path("users/update/<int:pk>/", user_views.update_user_profile, name="update_user_profile"),
    path("users/change-password/<int:pk>/", user_views.change_password, name="change_password"),
    path('users/upload-avatar/', avatar_views.upload_avatar, name='upload_avatar'),
    path('users/avatar/<int:user_id>/', avatar_views.get_avatar, name='get_avatar'),
    path('default-avatar/', avatar_views.get_default_avatar, name='get_default_avatar'),


]


""" urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/<int:pk>/', views.get_user, name='get_user'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:pk>/', views.update_user, name='update_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
] """