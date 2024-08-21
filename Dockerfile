FROM python:3.9-alpine3.13
LABEL maintainer="Paulo Lopera"

ENV PYTHONUNBUFFERED 1

# copy the requirements file to the /tmp directory in the container
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt ./tmp/requirements.dev.txt
COPY ./app /app
# WORKDIR is the directory where the CMD will be executed
WORKDIR /app 
EXPOSE 8000
# expose port 8000 to the outside world
ARG DEV=false
# run commands in single line to reduce the number of layers
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
# no password, no home directory, no login shell, and the username is django-user

ENV PATH="/py/bin:$PATH"

USER django-user
# switch to the user django-user specified in the adduser command