FROM python:latest

WORKDIR /usr/src/app

# Install Django
RUN apt update && apt upgrade -y
RUN python -m pip install Django

COPY ./runserver.sh /usr/bin/
RUN mkdir -p /usr/src/app/media
COPY ./default_avatar.jpg /usr/src/app/media/avatars/default_avatar.png

# Install project dependencies
RUN python -m pip install django djangorestframework
RUN python -m pip install django psycopg2
RUN python -m pip install django-cors-headers
RUN python -m pip install Pillow
RUN python -m pip install requests requests-oauthlib
RUN python -m pip install requests_oauthlib
RUN python -m pip install django-oauth-toolkit
RUN python -m pip install djangorestframework-simplejwt
RUN python -m pip install django-two-factor-auth qrcode
RUN python -m pip install django-otp
RUN python -m pip install phonenumbers
EXPOSE 8080

CMD [ "/usr/bin/runserver.sh" ]

