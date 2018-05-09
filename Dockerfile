FROM mdillon/postgis:10-alpine

MAINTAINER Brian.McKenna@rpsgroup.com

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
        py2-pip \
        py-setuptools \
    && apk add --no-cache --virtual .app-deps \
        dumb-init \
        py2-flask \
        py2-psycopg2 \
        supervisor \
    && pip install flask-cors \
    && cd / \
    && apk del .build-deps

COPY ./naccs.sql.gz /docker-entrypoint-initdb.d/naccs.sql.gz

COPY app.py /app.py
COPY start-app.sh /start-app.sh
COPY supervisor.conf /supervisor.conf

EXPOSE 3000

CMD ["dumb-init", "/usr/bin/supervisord", "-c", "/supervisor.conf"]
