# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import time

from flask import Blueprint, request, session, redirect, url_for, render_template, flash

from lwp.utils import query_db, hash_passwd, get_token, config

# TODO: see if we can move this block somewhere better
try:
    AUTH = config.get('global', 'auth')
    print(' * Auth type: ' + AUTH)
    if AUTH == 'ldap':
        import ldap
        LDAP_HOST = config.get('ldap', 'host')
        LDAP_PORT = int(config.get('ldap', 'port'))
        LDAP_PROTO = 'ldaps' if config.getboolean('ldap', 'ssl') else 'ldap'
        LDAP_BIND_METHOD = config.get('ldap', 'bind_method')
        LDAP_BASE = config.get('ldap', 'base')
        LDAP_BIND_DN = config.get('ldap', 'bind_dn')
        LDAP_PASS = config.get('ldap', 'password')
        ID_MAPPING = config.get('ldap', 'id_mapping')
        DISPLAY_MAPPING = config.get('ldap', 'display_mapping')
        OBJECT_CLASS = config.get('ldap', 'object_class')
        REQUIRED_GROUP = config.get('ldap', 'required_group')
    elif AUTH == 'htpasswd':
        HTPASSWD_FILE = config.get('htpasswd', 'file')
    elif AUTH == 'pam':
        import pam
        PAM_SERVICE = config.get('pam', 'service')
except NameError as err:
    print(' ! Revert to DB authentication ' + str(err))
    AUTH = 'database'


# Flask module
mod = Blueprint('auth', __name__)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_username = request.form['username']
        request_passwd = request.form['password']

        current_url = request.form['url']

        if AUTH == 'ldap':
            user = None
            try:
                l = ldap.initialize('%s://%s:%d' % (LDAP_PROTO, LDAP_HOST, LDAP_PORT))
                l.set_option(ldap.OPT_REFERRALS, 0)
                l.protocol_version = 3
                if LDAP_BIND_METHOD == 'user':
                    l.simple_bind(LDAP_BIND_DN, LDAP_PASS)
                else:
                    l.simple_bind()
                attrs = ['memberOf', ID_MAPPING, DISPLAY_MAPPING] if REQUIRED_GROUP else []
                q = l.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectClass=' + OBJECT_CLASS + ')(' + ID_MAPPING + '=' + request_username + '))', attrs)[0]
                is_member = False
                if 'memberOf' in q[1]:
                    for group in q[1]['memberOf']:
                        if group.find("cn=%s," % REQUIRED_GROUP) >= 0:
                            is_member = True
                            break
                if is_member is True or not REQUIRED_GROUP:
                    l.bind_s(q[0], request_passwd, ldap.AUTH_SIMPLE)
                    # set the parameters for user by ldap objectClass
                    user = {
                        'username': q[1][ID_MAPPING][0].decode('utf8'),
                        'name': q[1][DISPLAY_MAPPING][0].decode('utf8'),
                        'su': 'Yes'
                    }
            except Exception, e:
                print(str(e))
        elif AUTH == 'htpasswd':
            from lwp.utils import check_htpasswd
            user = None
            if check_htpasswd(HTPASSWD_FILE, request_username, request_passwd):
                user = {
                    'username': request_username,
                    'name': request_username,
                    'su': 'Yes'
                }
        elif AUTH == 'pam':
            user = None
            p = pam.pam()
            if p.authenticate(request_username, request_passwd, service=PAM_SERVICE):
                user = {
                    'username': request_username,
                    'name': request_username,
                    'su': 'Yes'
                }
        else:
            request_passwd = hash_passwd(request_passwd)
            user = query_db('select name, username, su from users where username=? and password=?', [request_username, request_passwd], one=True)

        if user:
            session['logged_in'] = True
            session['token'] = get_token()
            session['last_activity'] = int(time.time())
            session['username'] = user['username']
            session['name'] = user['name']
            session['su'] = user['su']
            flash(u'You are logged in!', 'success')

            if current_url == url_for('auth.login'):
                return redirect(url_for('main.home'))
            return redirect(current_url)

        flash(u'Invalid username or password!', 'error')
    return render_template('login.html', auth=AUTH)


@mod.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('token', None)
    session.pop('last_activity', None)
    session.pop('username', None)
    session.pop('name', None)
    session.pop('su', None)
    flash(u'You are logged out!', 'success')
    return redirect(url_for('auth.login'))
