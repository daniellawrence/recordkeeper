#!/usr/bin/env python
"""
This is a horrible, horrible way of generating a web gui for this.
It needs some love.
Would be really good to move this into a more MVC style with jinja2 templates.
"""

from flask import Flask, jsonify
app = Flask(__name__)

import api
import rc_exceptions
import settings
import re
import datetime
from bson.objectid import ObjectId


def debug(msg):
    """ If debug is enabled in the settings or local_settings.py then print a
    debug message to the console.
    """
    if settings.DEBUG:
        print("DEBUG: web.%(msg)s" % locals())


def encode_model(obj, recursive=False):
    """ Take a response from mongodb and turn it in to a json compilable object
    """

    if obj is None:
        #return obj
        return
    if isinstance(obj, int):
        out = obj
    elif isinstance(obj, (list)):
        out = [encode_model(item) for item in obj]
    elif isinstance(obj, (dict)):
        out = dict([(k, encode_model(v)) for (k, v) in obj.items()])
    elif isinstance(obj, datetime.datetime):
        out = str(obj)
    elif isinstance(obj, ObjectId):
        #out = {'ObjectId':str(obj)}
        out = str(obj)
    elif isinstance(obj, (str, unicode)):
        out = obj
    elif isinstance(obj, float):
        out = str(obj)
    else:
        raise TypeError(
           "Could not JSON-encode type '%s': %s" % (type(obj), str(obj))
        )
    return out


@app.route("/")
def index():
    format_list = ['html', 'json']
    response = []
    for format in format_list:
        response.append("<a href='/%(format)s'>%(format)s</a>" % locals())
    return "<Br />".join(response)


@app.route("/<format>/")
def format_index(format):
    record_list = api.find_records({})
    if format in ['python', 'json']:
        json_data = {'record_list': encode_model(record_list), 'query': {}}
        print json_data
        return jsonify(json_data)

    response = []
    for record in record_list:
        response.append("<a href='/html/record/%(name)s'>%(name)s</a> - <a href='/html/delete_record/%(name)s'>delete %(name)s</a>" % record)
    return "<Br />".join(response)


@app.route("/<format>/search/<query>")
def query_records(format, query, display_fields = None):
    debug("query_records(format='%(format)s' query='%(query)s' display_fields=%(display_fields)s)" % locals())
    if '&&' in query:
        query = " ".join
    try:
        record_list = api.find_records(query)
        record_list_count = len(record_list)
    except rc_exceptions.NoRecordsFound as error:
        return "%s" % error

    if format in ['python', 'json']:
        json_data = {
            'record_list': encode_model(record_list),
            'query': query,
            'display_fields': display_fields,
            'count': record_list_count
        }
        return jsonify(json_data)

    simple_format = None
    if display_fields:
        simple_format = re.sub('(?P<m>\w+)',"%(\g<m>)s", " ".join(display_fields))

    response = []
    for record in record_list:
        if simple_format:
            key_data = simple_format % record
            response.append("<a href='/html/record/%(name)s'>show %(name)s</a> - <a href='/html/delete_record/%(name)s'>delete %(name)s</a>" % record + key_data)
            continue
        response.append("<a href='/html/record/%(name)s'>show %(name)s</a> - <a href='/html/delete_record/%(name)s'>delete %(name)s</a>" % record)
    return "<Br />".join(response)


@app.route("/<format>/search/<query>/<display_fields>")
def query_records_with_display_fields(format,query, display_fields):
    debug("format=%(format)s query=%(query)s display_fields=%(display_fields)s" % locals())
    display_fields = display_fields.split(',')
    query += " name " + " ".join(display_fields)
    return query_records(format = format, query = query, display_fields = display_fields)    


@app.route("/<format>/record/<record_name>")
def find_record(format, record_name):
    try:
        record_list = api.find_records({'name': record_name})
    except rc_exceptions.NoRecordsFound as error:
        return str(error)

    if format in ['python', 'json']:
        json_data = encode_model(record_list[0])
        return jsonify(json_data)
    response = []
    for key, value in record_list[0].items():
        if value:
            response.append("<strong>%(key)s:</strong> %(value)s" % locals())
    return "<Br />".join(response)


@app.route("/<format>/add_record/<record_data>")
def insert_record(format, record_data):
    debug("add(format='%(format)s' record_data='%(record_data)s')" % locals())
    try:
        api.insert_record(record_data)
    except rc_exceptions.DuplicateRecord as error:
        return str(error)
    return query_records(format=format, query=record_data)


@app.route("/<format>/delete_record/<query>")
def delete_record(format, query):
    debug("delete_record(format='%(format)s' query='%(query)s')" % locals())
    try:
        api.delete_record({'name': query})
    except rc_exceptions.DuplicateRecord as error:
        return str(error)
    return "deleted: %(query)s" % locals()


@app.route("/<format>/update_record/<record_data>/where/<database_query>")
def update_record(format, record_data, database_query):
    debug("update_record(format='%(format)s' record_data='%(record_data)s' database_query='%(database_query)s')" % locals())
    api.update_record(database_query, record_data)
    return "updated record"
    #return query_records(format=format, query=database_query)

if __name__ == "__main__":
    app.debug = True
    app.run()
