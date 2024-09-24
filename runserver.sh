#!/bin/bash

sleep 5

python manage.py makemigrations app
python manage.py migrate

python manage.py runserver 0.0.0.0:8080
