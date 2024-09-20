FROM python:3

WORKDIR /usr/src/app

# Install Django
RUN apt update && apt upgrade -y
RUN python -m pip install Django

COPY ./runserver.sh /usr/bin/

# Install project dependencies
RUN pip install django djangorestframework
RUN pip install django psycopg2

EXPOSE 8080

CMD [ "/usr/bin/runserver.sh" ]
