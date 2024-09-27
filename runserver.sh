#!/bin/bash

sleep 5

python manage.py makemigrations api
python manage.py migrate
python pip install django-cors-headers

python manage.py runserver 0.0.0.0:8080
