from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)  # SERIAL en PostgreSQL se mapea a AutoField en Django
    email = models.EmailField(max_length=100, unique=True)  # VARCHAR(100), campo único
    password = models.TextField()  # TEXT para la contraseña cifrada
    username = models.CharField(max_length=50, unique=True)  # VARCHAR(50), campo único
    avatar = models.URLField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('in_game', 'In Game'),
        ('busy', 'Busy')
    ], default='offline')  # VARCHAR(20), con opciones
    created_at = models.DateTimeField(auto_now_add=True)  # TIMESTAMP, se establece automáticamente al crear el registro
    updated_at = models.DateTimeField(auto_now=True)  # TIMESTAMP, se actualiza automáticamente en cada modificación
    two_factor_auth = models.BooleanField(default=False)  # BOOLEAN para la autenticación de dos factores
    session_42 = models.TextField(blank=True, null=True)  # TEXT, para la ID de sesión de 42, puede ser nulo o estar en blanco


    def __str__(self):
        return self.username  # Esto es lo que se devolverá cuando conviertas el objeto en una cadena (por ejemplo, en el admin)

    class Meta:
        db_table = 'users'  # Opcional: especifica el nombre de la tabla en la base de datos

    



