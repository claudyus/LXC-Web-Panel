import sys
import time
import hashlib
import sqlite3
import ConfigParser

from flask import session, render_template, g, flash, redirect, url_for


# configuration
config = ConfigParser.SafeConfigParser()

try:
    # TODO: should really use with statement here rather than rely on cpython reference counting
    config.readfp(open('/etc/lwp/lwp.conf'))
except:
    # TODO: another blind exception
    print(' * missed /etc/lwp/lwp.conf file')
    try:
        # fallback on local config file
        config.readfp(open('lwp.conf'))
    except:
        print(' * cannot read config files. Exit!')
        sys.exit(1)


def connect_db(db_path):
    """
    SQLite3 connect function
    """
    return sqlite3.connect(db_path)


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def if_logged_in(function=render_template, f_args=('login.html', )):
    """
    helper decorator to verify if a user is logged
    """
    def decorator(handler):
        def new_handler(*args, **kwargs):
            if 'logged_in' in session:
                return handler(*args, **kwargs)
            else:
                return function(*f_args)
        new_handler.func_name = handler.func_name
        return new_handler
    return decorator


def get_bucket_token(container):
    query = query_db("SELECT bucket_token FROM machine WHERE machine_name=?", [container], one=True)
    if query is None:
        return ""
    else:
        return query['bucket_token']


def hash_passwd(passwd):
    return hashlib.sha512(passwd).hexdigest()


def get_token():
    return hashlib.md5(str(time.time())).hexdigest()


def check_session_limit():
    if 'logged_in' in session and session.get('last_activity') is not None:
        now = int(time.time())
        limit = now - 60 * int(config.get('session', 'time'))
        last_activity = session.get('last_activity')
        if last_activity < limit:
            flash(u'Session timed out !', 'info')
            redirect(url_for('logout'))
        else:
            session['last_activity'] = now
