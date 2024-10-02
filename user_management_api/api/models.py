from django.db import models
from django.contrib.auth.models import User as DjangoUser



# Create your models here.
class User(models.Model):
    friends = models.CharField(max_length=200, blank=True, null=True)
    friends_wait = models.CharField(max_length=200, blank=True, null=True)
    friends_request = models.CharField(max_length=200, blank=True, null=True)
    friends_blocked = models.CharField(max_length=200, blank=True, null=True)
    oauth_id = models.CharField(max_length=200, blank=True, null=True)
    user_42 = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_full_user_data(self):
        return {
            'id': self.id,
            'friends': self.friends,
            'friends_wait': self.friends_wait,
            'friends_request': self.friends_request,
            'friends_blocked': self.friends_blocked,
            'user_42': self.user_42,
            'oauth_id': self.oauth_id
        }

class ApiUser(models.Model):
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    avatar_image = models.ImageField(upload_to='avatars/', null=True, blank=True, default='default.jpg')
    friends = models.CharField(max_length=200, blank=True, null=True)
    friends_wait = models.CharField(max_length=200, blank=True, null=True) 
    friends_request = models.CharField(max_length=200, blank=True, null=True) 
    friends_blocked = models.CharField(max_length=200, blank=True, null=True)
    user_42 = models.BooleanField(default=False, blank=True, null=True)
    oauth_id = models.CharField(max_length=200, blank=True, null=True)

    def get_full_user_data(self):
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'friends': self.friends,
            'friends_wait': self.friends_wait,
            'friends_request': self.friends_wait,
            'friends_blocked': self.friends_blocked,
            'user_42': self.user_42,
            'oauth_id': self.oauth_id,
            'date_joined': self.user.date_joined,
            'last_login': self.user.last_login
        }
    def __str__(self):
        return self.user.username