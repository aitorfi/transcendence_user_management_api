FROM python:latest

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# Install Python dependencies
RUN pip install Django djangorestframework psycopg2-binary django-cors-headers Pillow django-oauth-toolkit requests-oauthlib

COPY ./runserver.sh /usr/bin/
RUN chmod +x /usr/bin/runserver.sh

COPY ./wait-for-it.sh /usr/bin/
RUN chmod +x /usr/bin/wait-for-it.sh

EXPOSE 8080

CMD ["/usr/bin/wait-for-it.sh", "postgres", "5432", "/usr/bin/runserver.sh"]