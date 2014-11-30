#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import sys

from flask import Flask, g

from lwp.utils import connect_db, check_session_limit, config
from lwp.views import main, auth, api

SESSION_SECRET_FILE = '/etc/lwp/session_secret'

if '--generate-session-secret' in sys.argv[1:]:
    key = os.urandom(24)
    with os.fdopen(os.open(SESSION_SECRET_FILE, os.O_WRONLY | os.O_CREAT, 0644), 'w') as handle:
        handle.write(key)
    exit(0)

try:
    SECRET_KEY = open(SESSION_SECRET_FILE, 'r').read()
except IOError:
    print(' * Missing session_secret file, your session will not survive server reboot. Run with --generate-session-secret to generate permanent file.')
    SECRET_KEY = os.urandom(24)

DEBUG = config.getboolean('global', 'debug')
DATABASE = config.get('database', 'file')
ADDRESS = config.get('global', 'address')
PORT = int(config.get('global', 'port'))
PREFIX = config.get('global', 'prefix')

# Flask app
app = Flask('lwp', static_url_path="{0}/static".format(PREFIX))
app.config.from_object(__name__)
app.register_blueprint(main.mod, url_prefix=PREFIX)
app.register_blueprint(auth.mod, url_prefix=PREFIX)
app.register_blueprint(api.mod, url_prefix=PREFIX)


if '--profiling' in sys.argv[1:]:
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.debug = True  # also enable debug


@app.before_request
def before_request():
    """
    executes functions before all requests
    """
    check_session_limit()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(app.config['DATABASE'])
    g.db = SQLAlchemy(app)


@app.teardown_request
def teardown_request(exception):
    """
    executes functions after all requests
    """
    if hasattr(g, 'db'):
        g.db.close()
