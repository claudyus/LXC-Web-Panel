# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import time

from flask import Blueprint, request, session, redirect, url_for, render_template, flash

from lwp.utils import get_token, read_config_file

import lwp.authenticators as auth

AUTH = read_config_file().get('global', 'auth')
AUTH_INSTANCE = auth.get_authenticator(AUTH)
print(' * Auth type: ' + AUTH)


# Flask module
mod = Blueprint('auth', __name__)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_username = request.form['username']
        request_passwd = request.form['password']

        current_url = request.form['url']

        user = AUTH_INSTANCE.authenticate(request_username, request_passwd)

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
