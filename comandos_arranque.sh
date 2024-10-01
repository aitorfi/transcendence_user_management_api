#!/bin/bash

# Ejecutar migraciones
docker exec -it user_management_api python manage.py makemigrations 
docker exec -it user_management_api python manage.py migrate

# Crear superusuario
docker exec -it user_management_api bash -c "DJANGO_SUPERUSER_USERNAME=root DJANGO_SUPERUSER_EMAIL=root@example.com DJANGO_SUPERUSER_PASSWORD=root python manage.py createsuperuser --noinput"

# Función para crear usuario
create_user() {
    curl -X POST http://localhost:50000/api/users/create/ \
         -H "Content-Type: application/json" \
         -d "{
             \"username\": \"$1\",
             \"email\": \"$2\",
             \"password\": \"$3\",
             \"first_name\": \"$4\",
             \"last_name\": \"$5\",
             \"age\": $6,
             \"avatar\": \"$7\",
             \"status\": \"$8\",
             \"two_factor_auth\": $9,
             \"session_42\": \"${10}\",
             \"friends\": \"${11}\",
             \"friends_wait\": \"${12}\"
         }"
    echo ""
}

# Crear usuarios
create_user "aitor" "aitor@gmail.com" "aitor" "Aitor" "Completo" 28 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "2-3" "0"
create_user "iker" "iker@gmail.com" "iker" "Iker" "Completo" 29 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "1-3" "0"
create_user "alejandro" "alejandro@gmail.com" "alejandro" "Alejandro" "Completo" 30 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "1-2" "0"
create_user "goiko" "goiko@gmail.com" "goiko" "Goiko" "Completo" 31 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "2-3" "0"