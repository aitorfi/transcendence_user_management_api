from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)  # SERIAL en PostgreSQL se mapea a AutoField en Django
    email = models.EmailField(max_length=100, unique=True)  # VARCHAR(100), campo único
    password = models.TextField()  # TEXT para la contraseña cifrada
    username = models.CharField(max_length=50, unique=True)  # VARCHAR(50), campo único

    def __str__(self):
        return self.username  # Esto es lo que se devolverá cuando conviertas el objeto en una cadena (por ejemplo, en el admin)

    #class Meta:
        #db_table = 'users'  # Opcional: especifica el nombre de la tabla en la base de datos