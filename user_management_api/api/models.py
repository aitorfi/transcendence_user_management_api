from django.db import models
from django.contrib.auth.models import User as DjangoUser



# Create your models here.
class User(models.Model):
    age = models.IntegerField()
    avatar = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('in_game', 'In Game'),
        ('busy', 'Busy')
    ], default='offline') 
    friends = models.CharField(max_length=200, blank=True, null=True)
    friends_wait = models.CharField(max_length=200, blank=True, null=True)
    two_factor_auth = models.BooleanField(default=False)  # BOOLEAN para la autenticación de dos factores
    session_42 = models.TextField(blank=True, null=True)  # TEXT, para la ID de sesión de 42, puede ser nulo o estar en blanco


    def __str__(self):
        return self.name

    def get_full_user_data(self):
        return {
            'id': self.id,
            'age': self.age,
            'avatar': self.avatar,
            'status': self.status,
            'friends': self.friends,
            'friends_wait': self.friends_wait,
            'two_factor_auth': self.two_factor_auth,
            'session_42': self.session_42
        }

class ApiUser(models.Model):
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    age = models.IntegerField(null=True, blank=True)
    avatar = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('in_game', 'In Game'),
        ('busy', 'Busy')
    ], default='offline')
    friends = models.CharField(max_length=200, blank=True, null=True)
    friends_wait = models.CharField(max_length=200, blank=True, null=True) 
    two_factor_auth = models.BooleanField(default=False)
    session_42 = models.TextField(blank=True, null=True)

    def get_full_user_data(self):
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'age': self.age,
            'avatar': self.avatar,
            'friends': self.friends,
            'friends_wait': self.friends_wait,
            'status': self.status,
            'two_factor_auth': self.two_factor_auth,
            'session_42': self.session_42,
            'date_joined': self.user.date_joined,
            'last_login': self.user.last_login
        }
    def __str__(self):
        return self.user.username