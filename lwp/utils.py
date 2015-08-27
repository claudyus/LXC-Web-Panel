import sys
import time
import hashlib
import sqlite3
import ConfigParser

from flask import session, render_template, g, flash, request, jsonify


"""
cgroup_ext is a data structure where for each input of edit.html we have an array with:
    position 0: the lxc container option to be saved on file
    position 1: the regex to validate the field
    position 2: the flash message to display on success.
"""
ip_regex = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
cidr_regex = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(\d|[1-2]\d|3[0-2]))*$'
file_match = '^\/\w[\w.\/-]+$'

cgroup_ext = {
    'arch': ['lxc.arch', '^(x86|i686|x86_64|amd64)$', ''],
    'utsname': ['lxc.utsname', '^\w[\w.-]+$', 'Hostname updated'],
    'type': ['lxc.network.type', '^(none|empty|veth|vlan|macvlan|phys)$', 'Link network type updated'],
    'link': ['lxc.network.link', '^[\w.-/]+$', 'Link name updated'],
    'flags': ['lxc.network.flags', '^(up|down)$', 'Network flag updated'],
    'hwaddr': ['lxc.network.hwaddr', '^[0-9a-fA-F:]+$', 'Hardware address updated'],
    'ipv4': ['lxc.network.ipv4', cidr_regex, 'IPv4 address updated'],
    'ipv4gw': ['lxc.network.ipv4.gateway', ip_regex, 'IPv4 gateway address updated'],
    'ipv6': ['lxc.network.ipv6', '^([0-9a-fA-F:/]+)+$', 'IPv6 address updated'],  # weak ipv6 regex check
    'ipv6gw': ['lxc.network.ipv6.gateway', '^([0-9a-fA-F:]+)+$', 'IPv6 gateway address updated'],
    'script_up': ['lxc.network.script.up', file_match, 'Network script down updated'],
    'script_down': ['lxc.network.script.down', file_match, 'Network script down updated'],
    'rootfs': ['lxc.rootfs', '^(\/|loop:\/|overlayfs:\/)[\w.\/:-]+$', 'Rootfs updated'],
    'memlimit': ['lxc.cgroup.memory.limit_in_bytes', '^([0-9]+|)$', 'Memory limit updated'],
    'swlimit': ['lxc.cgroup.memory.memsw.limit_in_bytes', '^([0-9]+|)$', 'Swap limit updated'],
    'cpus': ['lxc.cgroup.cpuset.cpus', '^[0-9,-]+$', 'CPUs updated'],
    'shares': ['lxc.cgroup.cpu.shares', '^[0-9]+$', 'CPU shares updated'],
    'deny': ['lxc.cgroup.devices.deny', '^$', '???'],
    'allow': ['lxc.cgroup.devices.allow', '^$', '???'],
    'loglevel': ['lxc.loglevel', '^[0-9]$', 'Log level updated'],
    'logfile': ['lxc.logfile', file_match, 'Log file updated'],
    'id_map': ['lxc.id_map', '^[ug0-9 ]+$', 'UID Mapping updated'],
    'hook_pre_start': ['lxc.hook.pre-start', file_match, 'Pre hook start updated'],
    'hook_pre_mount': ['lxc.hook.pre-mount', file_match, 'Pre mount hook updated'],
    'hook_mount': ['lxc.hook.mount', file_match, 'Mount hook updated'],
    'hook_start': ['lxc.hook.start', file_match, 'Container start hook updated'],
    'hook_post_stop': ['lxc.hook.post-stop', file_match, 'Container post hook updated'],
    'hook_clone': ['lxc.hook.clone', file_match, 'Container clone hook updated'],
    'start_auto': ['lxc.start.auto', '^(0|1)$', 'Autostart saved'],
    'start_delay': ['lxc.start.delay', '^[0-9]*$', 'Autostart delay option updated'],
    'start_order': ['lxc.start.order', '^[0-9]*$', 'Autostart order option updated']
}


# configuration
config = ConfigParser.SafeConfigParser()


def read_config_file():
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
    return config


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
                token = request.headers.get('Private-Token')
                result = query_db('select * from api_tokens where token=?', [token], one=True)
                if result is not None:
                    # token exists, access granted
                    return handler(*args, **kwargs)
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
            session.pop('logged_in', None)
            session.pop('token', None)
            session.pop('last_activity', None)
            session.pop('username', None)
            session.pop('name', None)
            session.pop('su', None)
            flash(u'You are logged out!', 'success')
        else:
            session['last_activity'] = now


def api_auth():
    """
    api decorator to verify if a token is valid
    """
    def decorator(handler):
        def new_handler(*args, **kwargs):
            token = request.args.get('private_token')
            if token is None:
                token = request.headers.get('Private-Token')
            if token:
                result = query_db('select * from api_tokens where token=?', [token], one=True)
                if result is not None:
                    # token exists, access granted
                    return handler(*args, **kwargs)
                else:
                    return jsonify(status="error", error="Unauthorized"), 401
            else:
                return jsonify(status="error", error="Unauthorized"), 401
        new_handler.func_name = handler.func_name
        return new_handler
    return decorator
