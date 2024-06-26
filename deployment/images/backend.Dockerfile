FROM python:3.10.11-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

RUN mkdir /app
WORKDIR /app

RUN apk add \
    --no-cache \
    musl-dev linux-headers gcc g++ git gettext postgresql-dev jpeg-dev zlib-dev libffi-dev libxslt-dev gdal-dev geos-dev proj-dev nodejs yarn openssh

COPY plataforma/requirements.txt /app/
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la carpeta plataforma/plataforma a /app/plataforma en la imagen
COPY plataforma/plataforma /app/plataforma

# Copiar manage.py a /app/ en la imagen
COPY plataforma/manage.py /app/
# COPY plataforma/src /app/src/
# COPY plataforma/statics /app/statics/

ARG VERSION
ENV VERSION $VERSION