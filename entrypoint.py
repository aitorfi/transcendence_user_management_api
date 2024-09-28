import subprocess
import time

def run_docker_command(container_name, command):
    escaped_command = command.replace('"', '\\"')
    full_command = [
        'docker', 'exec', '-i', container_name, 
        'python', 'manage.py', 'shell', '-c', 
        f'exec("""{escaped_command}""")'
    ]
    process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"Error ejecutando el comando: {' '.join(full_command)}")
        print(stderr.decode())
        exit(1)
    print(stdout.decode())

def run_manage_command(container_name, command):
    full_command = ['docker', 'exec', '-i', container_name, 'python', 'manage.py'] + command.split()
    subprocess.run(full_command, check=True)

def main():
    container_name = "user_management_api"
    
    # Ejecutar makemigrations para la app 'api'
    run_manage_command(container_name, "makemigrations api")
    time.sleep(1)
    
    # Ejecutar migrate
    run_manage_command(container_name, "migrate")
    time.sleep(1)

    # Crear superusuario
    create_superuser_command = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='root').exists():
    User.objects.create_superuser('root', 'admin@example.com', 'root')
    print("Superusuario creado con éxito.")
else:
    print("El superusuario 'admin' ya existe.")
"""
    run_docker_command(container_name, create_superuser_command)
    time.sleep(1)

    # Crear 10 usuarios (del 1 al 10)
    create_users_command = """
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from api.models import ApiUser

User = get_user_model()

for i in range(1, 11):
    username = f'user{i}'
    password = str(i)
    email = f'user{i}@example.com'
    
    if not User.objects.filter(username=username).exists():
        django_user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            first_name=f'User{i}',
            last_name='Dummy'
        )
        api_user = ApiUser.objects.create(
            user=django_user,
            age=30,  # Puedes ajustar esto según tus necesidades
            avatar='default_avatar.png',
            status='offline',
            two_factor_auth=False,
            session_42=None
        )
        print(f'Usuario {username} creado con éxito en Django y ApiUser.')
    else:
        print(f'El usuario {username} ya existe.')
"""
    run_docker_command(container_name, create_users_command)
    time.sleep(1)

    # Listar usuarios creados
    list_users_command = """
from api.models import ApiUser

api_users = ApiUser.objects.all()
print("Usuarios en ApiUser:")
for api_user in api_users:
    print(f"Username: {api_user.user.username}, Email: {api_user.user.email}")
"""
    run_docker_command(container_name, list_users_command)

    print("Todos los comandos se han ejecutado correctamente.")

if __name__ == "__main__":
    main()