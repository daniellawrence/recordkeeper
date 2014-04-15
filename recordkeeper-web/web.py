#!/usr/bin/env python
"""
This is a horrible, horrible way of generating a web gui for this.
It needs some love.
Would be really good to move this into a more MVC style with jinja2 templates.
"""

from flask import Flask, jsonify, render_template, request, redirect, Response
from bson.objectid import ObjectId
from markupsafe import Markup
from recordkeeper.api import find_records, list_keys

import json
import recordkeeper
import urllib

app = Flask(__name__)

recordkeeper.settings.DEBUG = True

import datetime


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


@app.route("/json/listkeys")
def json_listkeys():
    return Response(json.dumps(list_keys()),  mimetype='application/json')


def request_args(query=None):
    request_show = request.args.get('show')
    post_show = []
    query_list = []

    if request.method == 'POST':
        post_show = request.form['show']
        if post_show:
            post_show = post_show.split(' ')
        else:
            post_show = []

    if query:
        query_list = query.split()

    if request_show:
        request_show = request_show.split(' ')
    else:
        request_show = []

    show = request_show + post_show
    show += ['name', '_type']
    show = list(set(show))
    if query_list:
        show_filter = query_list
    else:
        show_filter = ["%s.defined" % s for s in show]
    print "show: %s" % show
    print "show_filter: %s" % show_filter
    return show, show_filter


@app.route('/', methods=['POST', 'GET'])
def index():
    """ basic list of all the objects. """
    show, show_filter = request_args()
    records = find_records(show + show_filter)
    print "records: %s" % records
    return render_template("index.html",
                           records=records,
                           show=show
    )


@app.route("/r/<name>")
def single_record(name):
    full_record = find_records("name=%s" % name)[0]
    return render_template("full_record.html",
                           full_record=sorted(full_record.items())
    )


@app.route("/s/<query>", methods=['POST', 'GET'])
def search(query):
    "Basic search"
    show, show_filter = request_args(query)
    records = find_records(show + show_filter)

    if len(records) == 1:
        record = records[0]
        record_name = record['name']
        return single_record(name=record_name)

    print "len(records): %d" % len(records)
    return render_template("index.html",
                           records=records,
                           query=query,
                           show=show
    )


@app.template_filter('urlencode')
def urlencode_filter(s):
    if isinstance(s, list):
        s = ','.join(s)
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


@app.template_filter('islist')
def islist_filter(s):
    if isinstance(s, list):
        return True
    return False

if __name__ == "__main__":
    app.debug = True
    app.run()
