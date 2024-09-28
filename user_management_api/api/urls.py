from django.urls import path, include
from .views import get_users, create_user, get_user, login_user, get_user_profile, sign_out_user 
#, oauth42_login, oauth42_callback
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
#from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path("users/", get_users, name="get_users"),
    path("users/<int:pk>/", get_user, name="get_user"),
    path("users/create/", create_user, name="create_user"),
    path('users/login/', login_user, name='login'),
    path('users/signout/', sign_out_user, name='signout'),
    path("users/profile/<int:pk>/", get_user_profile, name="get_user_profile"),
#    path('oauth/login/', oauth42_login, name='oauth42_login'),
#    path('oauth/callback/', oauth42_callback, name='oauth42_callback'),
#    path('2fa/', include(tf_urls)), # esto hay que cambiarlo para ajustarlo, pero como no se como va, tocara investigar
]

