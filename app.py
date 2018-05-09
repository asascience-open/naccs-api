#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import flask
import flask_cors
import json
import os
import psycopg2.extras
import psycopg2.pool
import urlparse

application = flask.Flask(__name__)
application.debug = os.environ.get('FLASK_DEBUG') in ['true', 'True']
app_version = os.environ.get('APP_VERSION')
flask_cors.CORS(application)

@application.route('/points')
def points():
    bbox = flask.request.args.get("bbox").split(',')
    if bbox is None:
        return ('bbox required', 400)
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id as id, ST_X(geom) as latitude, ST_Y(geom) as longitude" +
                       " FROM adcirc_save_points" +
                       " WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)" % tuple(bbox))
        data = cursor.fetchall()
        if len(data) > 0:
            return flask.jsonify({
                'points': map(lambda l: {
                    'id':        int(l[0]),
                    'longitude': float(l[1]),
                    'latitude':  float(l[2])
                },
                data)
            })
    return ('', 204)

@application.route('/points/<_id>', methods=['GET', 'OPTIONS'])
def point(_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT json FROM adcirc_save_points WHERE id=%s" % _id)
        data = cursor.fetchone()
        if data:
            return flask.jsonify(json.loads(data[0]))
    return ('', 204)

@application.route('/storms/<_id>')
def storm(_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT ST_AsGeoJSON(geom) from tropical_synthetic_storms" + 
                       " WHERE id=%s" % _id)
        data = cursor.fetchone()
        if data:
            data = json.loads(data[0])
            data.update({'id': _id})
            return flask.jsonify(data)
    return ('', 204)

@application.route('/docs')
def docs(path):
    return flask.redirect("http://docs.naccs.apiary.io", code=302)
@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def default(path):
    return flask.redirect("http://docs.naccs.apiary.io", code=302)

# PostgreSQL
url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
pool = psycopg2.pool.SimpleConnectionPool(
    minconn=0,
    maxconn=4,
    database=url.path[1:],
    host=url.hostname,
    port=url.port
)

@contextlib.contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextlib.contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=3000)
