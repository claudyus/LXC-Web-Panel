#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import lxclite as lxc
import lwp
import subprocess
import time
import re
import hashlib
import sqlite3
import os
import ConfigParser
import socket
import sys

# configuration
config = ConfigParser.SafeConfigParser()

try:
    config.readfp(open('/etc/lwp/lwp.conf'))
except:
    print ' * missed /etc/lwp/lwp.conf file'
    try:
        # fallback on local config file
        config.readfp(open('lwp.conf'))
    except:
        print ' * cannot read config files. Exit!'
        sys.exit(1)

SECRET_KEY = '\xb13\xb6\xfb+Z\xe8\xd1n\x80\x9c\xe7KM\x1c\xc1\xa7\xf8\xbeY\x9a\xfa<.'

DEBUG = config.getboolean('global', 'debug')
DATABASE = config.get('database', 'file')
ADDRESS = config.get('global', 'address')
PORT = int(config.get('global', 'port'))
try:
    SSL = bool(config.get('global', 'ssl'))
    PKEY = config.get('global', 'pkey')
    CERT = config.get('global', 'cert')
    if not os.path.isfile(PKEY) or not os.path.isfile(CERT):
        SSL = False
except ConfigParser.NoOptionError:
    SSL = False
    print "- SSL feature disabled"

try:
    USE_BUCKET = bool(config.get('global', 'buckets'))
    BUCKET_HOST = config.get('buckets', 'buckets_host')
    BUCKET_PORT = config.get('buckets', 'buckets_port')
except:
    USE_BUCKET = False
    print "- Bucket feature disabled"

try:
    AUTH = config.get('global', 'auth')
    print ' * Auth type: ' + AUTH
    if (AUTH == 'ldap'):
        import ldap
        LDAP_HOST = config.get('ldap', 'host')
        LDAP_PORT = int(config.get('ldap', 'port'))
        LDAP_BASE = config.get('ldap', 'base')
        LDAP_BIND_DN = config.get('ldap', 'bind_dn')
        LDAP_PASS = config.get('ldap', 'password')
except NameError as err:
    print ' ! Revert to DB authentication ' + err
    AUTH = 'database'

storage_repos = config.items('storage_repository')

# Flask app
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    '''
    SQLite3 connect function
    '''
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    '''
    executes functions before all requests
    '''
    check_session_limit()
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    '''
    executes functions after all requests
    '''
    if hasattr(g, 'db'):
        g.db.close()


def if_logged_in(function=render_template, f_args=('login.html', )):
    '''
    helper decorator to verify if a user is logged
    '''
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


@app.route('/')
@app.route('/home')
@if_logged_in()
def home():
    '''
    home page function
    '''
    listx = lxc.listx()
    containers_all = []

    for status in ['RUNNING', 'FROZEN', 'STOPPED']:
        containers_by_status = []

        for container in listx[status]:
            containers_by_status.append({
                'name': container,
                'memusg': lwp.memory_usage(container),
                'settings': lwp.get_container_settings(container),
                'ipv4': lxc.get_ipv4(container),
                'bucket': get_bucket_token(container)
            })
        containers_all.append({
            'status': status.lower(),
            'containers': containers_by_status
        })

    return render_template('index.html', containers=lxc.ls(), containers_all=containers_all, dist=lwp.check_ubuntu(), host=socket.gethostname(), templates=lwp.get_templates_list(), storage_repos=storage_repos, auth=AUTH)


@app.route('/about')
@if_logged_in()
def about():
    '''
    about page
    '''
    return render_template('about.html', containers=lxc.ls(), version=lwp.check_version())


@app.route('/<container>/edit', methods=['POST', 'GET'])
@if_logged_in()
def edit(container=None):
    '''
    edit containers page and actions if form post request
    '''
    host_memory = lwp.host_memory_usage()
    cfg = lwp.get_container_settings(container)
    # read config also from databases
    cfg['bucket'] = get_bucket_token(container)

    if request.method == 'POST':
        ip_regex = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(/(3[0-2]|[12]?[0-9]))?'
        info = lxc.info(container)

        form = {}
        form['type'] = request.form['type']
        form['link'] = request.form['link']
        try:
            form['flags'] = request.form['flags']
        except KeyError:
            form['flags'] = 'down'
        form['hwaddr'] = request.form['hwaddress']
        form['rootfs'] = request.form['rootfs']
        form['utsname'] = request.form['hostname']
        form['ipv4'] = request.form['ipaddress']
        form['memlimit'] = request.form['memlimit']
        form['swlimit'] = request.form['swlimit']
        form['cpus'] = request.form['cpus']
        form['shares'] = request.form['cpushares']
        form['bucket'] = request.form['bucket']
        try:
            form['autostart'] = request.form['autostart']
        except KeyError:
            form['autostart'] = False

        if form['utsname'] != cfg['utsname'] and re.match('(?!^containers$)|^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$', form['utsname']):
            lwp.push_config_value('lxc.utsname', form['utsname'], container=container)
            flash(u'Hostname updated for %s!' % container, 'success')

        if form['flags'] != cfg['flags'] and re.match('^(up|down)$', form['flags']):
            lwp.push_config_value('lxc.network.flags', form['flags'], container=container)
            flash(u'Network flag updated for %s!' % container, 'success')

        if form['type'] != cfg['type'] and re.match('^\w+$', form['type']):
            lwp.push_config_value('lxc.network.type', form['type'], container=container)
            flash(u'Link type updated for %s!' % container, 'success')

        if form['link'] != cfg['link'] and re.match('^[a-zA-Z0-9_-]+$', form['link']):
            lwp.push_config_value('lxc.network.link', form['link'], container=container)
            flash(u'Link name updated for %s!' % container, 'success')

        if form['hwaddr'] != cfg['hwaddr'] and re.match('^([a-fA-F0-9]{2}[:|\-]?){6}$', form['hwaddr']):
            lwp.push_config_value('lxc.network.hwaddr', form['hwaddr'], container=container)
            flash(u'Hardware address updated for %s!' % container, 'success')

        if (not form['ipv4'] and form['ipv4'] != cfg['ipv4']) or (form['ipv4'] != cfg['ipv4'] and re.match('^%s$' % ip_regex, form['ipv4'])):
            lwp.push_config_value('lxc.network.ipv4', form['ipv4'], container=container)
            flash(u'IP address updated for %s!' % container, 'success')

        if form['memlimit'] != cfg['memlimit'] and form['memlimit'].isdigit() and int(form['memlimit']) <= int(host_memory['total']):
            if int(form['memlimit']) == int(host_memory['total']):
                form['memlimit'] = ''

            if form['memlimit'] != cfg['memlimit']:
                lwp.push_config_value('lxc.cgroup.memory.limit_in_bytes', form['memlimit'], container=container)
                if info["state"].lower() != 'stopped':
                    lxc.cgroup(container, 'lxc.cgroup.memory.limit_in_bytes', form['memlimit'])
                flash(u'Memory limit updated for %s!' % container, 'success')

        if form['swlimit'] != cfg['swlimit'] and form['swlimit'].isdigit() and int(form['swlimit']) <= int(host_memory['total'] * 2):
            if int(form['swlimit']) == int(host_memory['total'] * 2):
                form['swlimit'] = ''

            if form['swlimit'].isdigit():
                form['swlimit'] = int(form['swlimit'])

            if form['memlimit'].isdigit():
                form['memlimit'] = int(form['memlimit'])

            if (form['memlimit'] == '' and form['swlimit'] != '') or (form['memlimit'] > form['swlimit'] and form['swlimit'] != ''):
                flash(u'Can\'t assign swap memory lower than the memory limit', 'warning')

            elif form['swlimit'] != cfg['swlimit'] and form['memlimit'] <= form['swlimit']:
                lwp.push_config_value('lxc.cgroup.memory.memsw.limit_in_bytes', form['swlimit'], container=container)
                if info["state"].lower() != 'stopped':
                    lxc.cgroup(container, 'lxc.cgroup.memory.memsw.limit_in_bytes', form['swlimit'])
                flash(u'Swap limit updated for %s!' % container, 'success')

        if (not form['cpus'] and form['cpus'] != cfg['cpus']) or (form['cpus'] != cfg['cpus'] and re.match('^[0-9,-]+$', form['cpus'])):
            lwp.push_config_value('lxc.cgroup.cpuset.cpus', form['cpus'], container=container)
            if info["state"].lower() != 'stopped':
                    lxc.cgroup(container, 'lxc.cgroup.cpuset.cpus', form['cpus'])
            flash(u'CPUs updated for %s!' % container, 'success')

        if (not form['shares'] and form['shares'] != cfg['shares']) or (form['shares'] != cfg['shares'] and re.match('^[0-9]+$', form['shares'])):
            lwp.push_config_value('lxc.cgroup.cpu.shares', form['shares'], container=container)
            if info["state"].lower() != 'stopped':
                    lxc.cgroup(container, 'lxc.cgroup.cpu.shares', form['shares'])
            flash(u'CPU shares updated for %s!' % container, 'success')

        if form['rootfs'] != cfg['rootfs'] and re.match('^[a-zA-Z0-9_/\-]+', form['rootfs']):
            lwp.push_config_value('lxc.rootfs', form['rootfs'], container=container)
            flash(u'Rootfs updated!' % container, 'success')

        if bool(form['autostart']) != bool(cfg['auto']):
            lwp.push_config_value('lxc.start.auto', 1 if form['autostart'] else 0, container=container)
            flash(u'Autostart saved for %s' % container, 'success')

        if form['bucket'] != cfg['bucket']:
            g.db.execute("INSERT INTO machine(machine_name, bucket_token) VALUES (?, ?)", [container, form['bucket']])
            g.db.commit()
            flash(u'Bucket config for %s saved!' % container, 'success')

    info = lxc.info(container)
    status = info['state']
    pid = info['pid']

    infos = {'status': status, 'pid': pid, 'memusg': lwp.memory_usage(container)}
    return render_template('edit.html', containers=lxc.ls(), container=container, infos=infos, settings=cfg, host_memory=host_memory, storage_repos=storage_repos)


@app.route('/settings/lxc-net', methods=['POST', 'GET'])
@if_logged_in()
def lxc_net():
    '''
    lxc-net (/etc/default/lxc) settings page and actions if form post request
    '''
    if session['su'] != 'Yes':
        return abort(403)

    if request.method == 'POST':
        if lxc.running() == []:
            cfg = lwp.get_net_settings()
            ip_regex = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

            form = {}
            for key in ['bridge', 'address', 'netmask', 'network', 'range', 'max']:
                form[key] = request.form.get(key, None)
            form['use'] = request.form.get('use', None)

            if form['use'] != cfg['use']:
                lwp.push_net_value('USE_LXC_BRIDGE', 'true' if form['use'] else 'false')

            if form['bridge'] and form['bridge'] != cfg['bridge'] and re.match('^[a-zA-Z0-9_-]+$', form['bridge']):
                lwp.push_net_value('LXC_BRIDGE', form['bridge'])

            if form['address'] and form['address'] != cfg['address'] and re.match('^%s$' % ip_regex, form['address']):
                lwp.push_net_value('LXC_ADDR', form['address'])

            if form['netmask'] and form['netmask'] != cfg['netmask'] and re.match('^%s$' % ip_regex, form['netmask']):
                lwp.push_net_value('LXC_NETMASK', form['netmask'])

            if form['network'] and form['network'] != cfg['network'] and re.match('^%s(?:/\d{1,2}|)$' % ip_regex, form['network']):
                lwp.push_net_value('LXC_NETWORK', form['network'])

            if form['range'] and form['range'] != cfg['range'] and re.match('^%s,%s$' % (ip_regex, ip_regex), form['range']):
                lwp.push_net_value('LXC_DHCP_RANGE', form['range'])

            if form['max'] and form['max'] != cfg['max'] and re.match('^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', form['max']):
                lwp.push_net_value('LXC_DHCP_MAX', form['max'])

            if lwp.net_restart() == 0:
                flash(u'LXC Network settings applied successfully!', 'success')
            else:
                flash(u'Failed to restart LXC networking.', 'error')
        else:
            flash(u'Stop all containers before restart lxc-net.', 'warning')
    return render_template('lxc-net.html', containers=lxc.ls(), cfg=lwp.get_net_settings(), running=lxc.running())


@app.route('/lwp/users', methods=['POST', 'GET'])
@if_logged_in()
def lwp_users():
    '''
    returns users and get posts request : can edit or add user in page.
    this funtction uses sqlite3
    '''
    if session['su'] != 'Yes':
        return abort(403)

    if (AUTH == 'ldap'):
        return abort(403, 'You are using ldap as AUTH backend.')

    try:
        trash = request.args.get('trash')
    except KeyError:
        trash = 0

    su_users = query_db("SELECT COUNT(id) as num FROM users WHERE su='Yes'", [], one=True)

    if request.args.get('token') == session.get('token') and int(trash) == 1 and request.args.get('userid') and request.args.get('username'):
        nb_users = query_db("SELECT COUNT(id) as num FROM users", [], one=True)

        if nb_users['num'] > 1:
            if su_users['num'] <= 1:
                su_user = query_db("SELECT username FROM users WHERE su='Yes'", [], one=True)

                if su_user['username'] == request.args.get('username'):
                    flash(u'Can\'t delete the last admin user : %s' % request.args.get('username'), 'error')
                    return redirect(url_for('lwp_users'))

            g.db.execute("DELETE FROM users WHERE id=? AND username=?", [request.args.get('userid'), request.args.get('username')])
            g.db.commit()
            flash(u'Deleted %s' % request.args.get('username'), 'success')
            return redirect(url_for('lwp_users'))

        flash(u'Can\'t delete the last user!', 'error')
        return redirect(url_for('lwp_users'))

    if request.method == 'POST':
        users = query_db('SELECT id, name, username, su FROM users ORDER BY id ASC')

        if request.form['newUser'] == 'True':
            if not request.form['username'] in [user['username'] for user in users]:
                if re.match('^\w+$', request.form['username']) and request.form['password1']:
                    if request.form['password1'] == request.form['password2']:
                        if request.form['name']:
                            if re.match('[a-z A-Z0-9]{3,32}', request.form['name']):
                                g.db.execute("INSERT INTO users (name, username, password) VALUES (?, ?, ?)", [request.form['name'], request.form['username'], hash_passwd(request.form['password1'])])
                                g.db.commit()
                            else:
                                flash(u'Invalid name!', 'error')
                        else:
                            g.db.execute("INSERT INTO users (username, password) VALUES (?, ?)", [request.form['username'], hash_passwd(request.form['password1'])])
                            g.db.commit()

                        flash(u'Created %s' % request.form['username'], 'success')
                    else:
                        flash(u'No password match', 'error')
                else:
                    flash(u'Invalid username or password!', 'error')
            else:
                flash(u'Username already exist!', 'error')

        elif request.form['newUser'] == 'False':
            if request.form['password1'] == request.form['password2']:
                if re.match('[a-z A-Z0-9]{3,32}', request.form['name']):
                    if su_users['num'] <= 1:
                        su = 'Yes'
                    else:
                        try:
                            su = request.form['su']
                        except KeyError:
                            su = 'No'

                    if not request.form['name']:
                        g.db.execute("UPDATE users SET name='', su=? WHERE username=?", [su, request.form['username']])
                        g.db.commit()
                    elif request.form['name'] and not request.form['password1'] and not request.form['password2']:
                        g.db.execute("UPDATE users SET name=?, su=? WHERE username=?", [request.form['name'], su, request.form['username']])
                        g.db.commit()
                    elif request.form['name'] and request.form['password1'] and request.form['password2']:
                        g.db.execute("UPDATE users SET name=?, password=?, su=? WHERE username=?", [request.form['name'], hash_passwd(request.form['password1']), su, request.form['username']])
                        g.db.commit()
                    elif request.form['password1'] and request.form['password2']:
                        g.db.execute("UPDATE users SET password=?, su=? WHERE username=?", [hash_passwd(request.form['password1']), su, request.form['username']])
                        g.db.commit()

                    flash(u'Updated', 'success')
                else:
                    flash(u'Invalid name!', 'error')
            else:
                flash(u'No password match', 'error')
        else:
            flash(u'Unknown error!', 'error')

    users = query_db("SELECT id, name, username, su FROM users ORDER BY id ASC")
    nb_users = query_db("SELECT COUNT(id) as num FROM users", [], one=True)
    su_users = query_db("SELECT COUNT(id) as num FROM users WHERE su='Yes'", [], one=True)

    return render_template('users.html', containers=lxc.ls(), users=users, nb_users=nb_users, su_users=su_users)


@app.route('/checkconfig')
@if_logged_in()
def checkconfig():
    '''
    returns the display of lxc-checkconfig command
    '''
    if session['su'] != 'Yes':
        return abort(403)

    return render_template('checkconfig.html', containers=lxc.ls(), cfg=lxc.checkconfig())


@app.route('/action', methods=['GET'])
@if_logged_in()
def action():
    '''
    manage all actions related to containers
    lxc-start, lxc-stop, etc...
    '''
    if request.args['token'] == session.get('token'):
        action = request.args['action']
        name = request.args['name']

        if action == 'start':
            try:
                if lxc.start(name) == 0:
                    time.sleep(1)  # Fix bug : "the container is randomly not displayed in overview list after a boot"
                    flash(u'Container %s started successfully!' % name, 'success')
                else:
                    flash(u'Unable to start %s!' % name, 'error')
            except lxc.ContainerAlreadyRunning:
                flash(u'Container %s is already running!' % name, 'error')
        elif action == 'stop':
            try:
                if lxc.stop(name) == 0:
                    flash(u'Container %s stopped successfully!' % name, 'success')
                else:
                    flash(u'Unable to stop %s!' % name, 'error')
            except lxc.ContainerNotRunning:
                flash(u'Container %s is already stopped!' % name, 'error')
        elif action == 'freeze':
            try:
                if lxc.freeze(name) == 0:
                    flash(u'Container %s frozen successfully!' % name, 'success')
                else:
                    flash(u'Unable to freeze %s!' % name, 'error')
            except lxc.ContainerNotRunning:
                flash(u'Container %s not running!' % name, 'error')
        elif action == 'unfreeze':
            try:
                if lxc.unfreeze(name) == 0:
                    flash(u'Container %s unfrozen successfully!' % name, 'success')
                else:
                    flash(u'Unable to unfeeze %s!' % name, 'error')
            except lxc.ContainerNotRunning:
                flash(u'Container %s not frozen!' % name, 'error')
        elif action == 'destroy':
            if session['su'] != 'Yes':
                return abort(403)
            try:
                if lxc.destroy(name) == 0:
                    flash(u'Container %s destroyed successfully!' % name, 'success')
                else:
                    flash(u'Unable to destroy %s!' % name, 'error')
            except lxc.ContainerDoesntExists:
                flash(u'The Container %s does not exists!' % name, 'error')
        elif action == 'reboot' and name == 'host':
            if session['su'] != 'Yes':
                return abort(403)
            msg = '\v*** LXC Web Panel *** \
                    \nReboot from web panel'
            try:
                subprocess.check_call('/sbin/shutdown -r now \'%s\'' % msg, shell=True)
                flash(u'System will now restart!', 'success')
            except:
                flash(u'System error!', 'error')
        elif action == 'push':
            pass
    try:
        if request.args['from'] == 'edit':
            return redirect('../%s/edit' % name)
        else:
            return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))


@app.route('/action/create-container', methods=['GET', 'POST'])
@if_logged_in()
def create_container():
    '''
    verify all forms to create a container
    '''
    if session['su'] != 'Yes':
        return abort(403)
    if request.method == 'POST':
        name = request.form['name']
        template = request.form['template']
        command = request.form['command']

        if re.match('^(?!^containers$)|[a-zA-Z0-9_-]+$', name):
            storage_method = request.form['backingstore']

            if storage_method == 'default':
                try:
                    if lxc.create(name, template=template, xargs=command) == 0:
                        flash(u'Container %s created successfully!' % name, 'success')
                    else:
                        flash(u'Failed to create %s!' % name, 'error')
                except lxc.ContainerAlreadyExists:
                    flash(u'The Container %s is already created!' % name, 'error')
                except subprocess.CalledProcessError:
                    flash(u'Error!' % name, 'error')

            elif storage_method == 'directory':
                directory = request.form['dir']

                if re.match('^/[a-zA-Z0-9_/-]+$', directory) and directory != '':
                    try:
                        if lxc.create(name, template=template, storage='dir --dir %s' % directory, xargs=command) == 0:
                            flash(u'Container %s created successfully!' % name, 'success')
                        else:
                            flash(u'Failed to create %s!' % name, 'error')
                    except lxc.ContainerAlreadyExists:
                        flash(u'The Container %s is already created!' % name, 'error')
                    except subprocess.CalledProcessError:
                        flash(u'Error!' % name, 'error')

            elif storage_method == 'zfs':
                zfs = request.form['zpoolname']

                if re.match('^[a-zA-Z0-9_-]+$', zfs) and zfs != '':
                    try:
                        if lxc.create(name, template=template, storage='zfs --zfsroot %s' % zfs, xargs=command) == 0:
                            flash(u'Container %s created successfully!' % name, 'success')
                        else:
                            flash(u'Failed to create %s!' % name, 'error')
                    except lxc.ContainerAlreadyExists:
                        flash(u'The Container %s is already created!' % name, 'error')
                    except subprocess.CalledProcessError:
                        flash(u'Error!' % name, 'error')

            elif storage_method == 'lvm':
                lvname = request.form['lvname']
                vgname = request.form['vgname']
                fstype = request.form['fstype']
                fssize = request.form['fssize']
                storage_options = 'lvm'

                if re.match('^[a-zA-Z0-9_-]+$', lvname) and lvname != '':
                    storage_options += ' --lvname %s' % lvname
                if re.match('^[a-zA-Z0-9_-]+$', vgname) and vgname != '':
                    storage_options += ' --vgname %s' % vgname
                if re.match('^[a-z0-9]+$', fstype) and fstype != '':
                    storage_options += ' --fstype %s' % fstype
                if re.match('^[0-9][G|M]$', fssize) and fssize != '':
                    storage_options += ' --fssize %s' % fssize

                try:
                    if lxc.create(name, template=template, storage=storage_options, xargs=command) == 0:
                        flash(u'Container %s created successfully!' % name, 'success')
                    else:
                        flash(u'Failed to create %s!' % name, 'error')
                except lxc.ContainerAlreadyExists:
                    flash(u'The container/logical volume %s is already created!' % name, 'error')
                except subprocess.CalledProcessError:
                    flash(u'Error!' % name, 'error')

            else:
                flash(u'Missing parameters to create container!', 'error')

        else:
            if name == '':
                flash(u'Please enter a container name!', 'error')
            else:
                flash(u'Invalid name for \"%s\"!' % name, 'error')

    return redirect(url_for('home'))


@app.route('/action/clone-container', methods=['GET', 'POST'])
@if_logged_in()
def clone_container():
    '''
    verify all forms to clone a container
    '''
    if session['su'] != 'Yes':
        return abort(403)
    if request.method == 'POST':
        orig = request.form['orig']
        name = request.form['name']

        try:
            snapshot = request.form['snapshot']
            if snapshot == 'True':
                snapshot = True
        except KeyError:
            snapshot = False

        if re.match('^(?!^containers$)|[a-zA-Z0-9_-]+$', name):
            out = None

            try:
                out = lxc.clone(orig=orig, new=name, snapshot=snapshot)
            except lxc.ContainerAlreadyExists:
                flash(u'The Container %s already exists!' % name, 'error')
            except subprocess.CalledProcessError:
                flash(u'Can\'t snapshot a directory', 'error')

            if out and out == 0:
                flash(u'Container %s cloned into %s successfully!' % (orig, name), 'success')
            elif out and out != 0:
                flash(u'Failed to clone %s into %s!' % (orig, name), 'error')

        else:
            if name == '':
                flash(u'Please enter a container name!', 'error')
            else:
                flash(u'Invalid name for \"%s\"!' % name, 'error')

    return redirect(url_for('home'))


@app.route('/action/backup-container', methods=['GET', 'POST'])
@if_logged_in()
def backup_container():
    '''
    Verify the form to backup a container
    '''
    if request.method == 'POST':
        container = request.form['orig']
        sr_type = request.form['dest']
        push = request.form['push']
        for sr in storage_repos:
            if sr_type in sr:
                sr_path = sr[1]
                break
            else:
                sr_path = None

        out = None

        try:
            backup_file = lxc.backup(container=container, sr_type=sr_type, destination=sr_path)
            bucket_token = get_bucket_token(container)
            if push and bucket_token and USE_BUCKET:
                    os.system('curl http://{}:{}/{} -F file=@{}'.format(BUCKET_HOST, BUCKET_PORT, bucket_token, backup_file))
        except lxc.ContainerDoesntExists:
            flash(u'The Container %s does not exist !' % container, 'error')
        except lxc.DirectoryDoesntExists:
            flash(u'Local backup directory "%s" does not exist !' % sr_path, 'error')
        except lxc.NFSDirectoryNotMounted:
            flash(u'NFS repository "%s" not mounted !' % sr_path, 'error')
        except subprocess.CalledProcessError:
            flash(u'Error during transfert !', 'error')
        except:
            flash(u'Error during transfert !', 'error')

        if out == 0:
            flash(u'Container %s backed up successfully' % container, 'success')
        elif out != 0:
            flash(u'Failed to backup %s container' % container, 'error')

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_username = request.form['username']
        request_passwd = request.form['password']

        current_url = request.form['url']

        if (AUTH == 'ldap'):
            try:
                l = ldap.open(LDAP_HOST, LDAP_PORT)
                l.set_option(ldap.OPT_REFERRALS, 0)
                l.protocol_version = 3
                l.simple_bind(LDAP_BIND_DN, LDAP_PASS)
                q = l.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, '(&(objectClass=user)(sAMAccountName=' + request_username + '))', [])[0]
                l.bind_s(q[0], request_passwd, ldap.AUTH_SIMPLE)
                #set the parameters for user by ldap objectClass
                user = {}
                user['username'] = q[1]['sAMAccountName'][0].decode('utf8')
                user['name'] = q[1]['displayName'][0].decode('utf8')
                user['su'] = 'Yes'   # on ldap all user are admin
            except Exception, e:
                print str(e)
                user = None
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

            if current_url == url_for('login'):
                return redirect(url_for('home'))
            return redirect(current_url)

        flash(u'Invalid username or password!', 'error')
    return render_template('login.html', auth=AUTH)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('token', None)
    session.pop('last_activity', None)
    session.pop('username', None)
    session.pop('name', None)
    session.pop('su', None)
    flash(u'You are logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/_refresh_cpu_host')
@if_logged_in()
def refresh_cpu_host():
    return lwp.host_cpu_percent()


@app.route('/_refresh_uptime_host')
@if_logged_in()
def refresh_uptime_host():
    return jsonify(lwp.host_uptime())


@app.route('/_refresh_disk_host')
@if_logged_in()
def refresh_disk_host():
    return jsonify(lwp.host_disk_usage(partition=config.get('overview', 'partition')))


@app.route('/_refresh_memory_<name>')
@if_logged_in()
def refresh_memory_containers(name=None):
    if name == 'containers':
        containers_running = lxc.running()
        containers = []
        for container in containers_running:
            container = container.replace(' (auto)', '')
            containers.append({'name': container, 'memusg': lwp.memory_usage(container), 'settings': lwp.get_container_settings(container)})
        return jsonify(data=containers)
    elif name == 'host':
        return jsonify(lwp.host_memory_usage())
    return jsonify({'memusg': lwp.memory_usage(name)})


@app.route('/_check_version')
@if_logged_in()
def check_version():
    return jsonify(lwp.check_version())


def hash_passwd(passwd):
    return hashlib.sha512(passwd).hexdigest()


def get_token():
    return hashlib.md5(str(time.time())).hexdigest()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def check_session_limit():
    if 'logged_in' in session and session.get('last_activity') is not None:
        now = int(time.time())
        limit = now - 60 * int(config.get('session', 'time'))
        last_activity = session.get('last_activity')
        if last_activity < limit:
            flash(u'Session timed out !', 'info')
            logout()
        else:
            session['last_activity'] = now


#####################################
#   API implementation
#####################################


def api_auth():
    '''
    api decorator to verify if a token is valid
    '''
    def decorator(handler):
        def new_handler(*args, **kwargs):
            token = request.args.get('private_token')
            if token is None:
                token = request.headers['Private-Token']
            result = query_db('select * from api_tokens where token=?', [token], one=True)
            if result is not None:
                #token exists, access granted
                return handler(*args, **kwargs)
            else:
                return jsonify(status="error", error="Unauthorized"), 401
        new_handler.func_name = handler.func_name
        return new_handler
    return decorator


@app.route('/api/v1/containers')
@api_auth()
def get_containers():
    '''
    Returns lxc containers on the current machine and brief status information.
    '''
    listx = lxc.listx()
    return jsonify(listx)


@app.route('/api/v1/container/<name>')
@api_auth()
def get_container(name):
    return jsonify(lxc.info(name))


@app.route('/api/v1/container/<name>', methods=['POST'])
@api_auth()
def post_container(name):
    data = request.get_json(force=True)
    if data is None:
        return jsonify(status="error", error="Bad request"), 400

    status = data['action']
    try:
        if status == "stop":
            lxc.stop(name)
            return jsonify(status="ok"), 200
        elif status == "start":
            lxc.start(name)
            return jsonify(status="ok"), 200
        elif status == "freeze":
            lxc.freeze(name)
            return jsonify(status="ok"), 200
 
        return jsonify(status="error", error="Bad request"), 400
    except lxc.ContainerDoesntExists:
        return jsonify(status="error", error="Container doesn' t exists"), 409


@app.route('/api/v1/container/', methods=['PUT'])
@api_auth()
def add_container():
    data = request.get_json(force=True)
    if data is None:
        return jsonify(status="error", error="Bad request"), 400

    if (bool('template' not in data) != bool('clone' not in data)) | bool('name' not in data):
        return jsonify(status="error", error="Bad request"), 400

    print data
    if 'template' in data:
        # we want a new container
        if 'store' not in data:
            data.update(store=None)
        if 'xargs' not in data:
            data.update(xargs=None)

        try:
            lxc.create(data.name, data.template, data.store, data.xargs)
        except lxc.ContainerAlreadyExists:
            return jsonify(status="error", error="Container yet exists"), 409
    else:
        #we want to clone a container
        try:
            lxc.clone(data.clone, data.name)
        except lxc.ContainerAlreadyExists:
            return jsonify(status="error", error="Container yet exists"), 409
        except:
            abort(500)
    return jsonify(status="ok"), 200


@app.route('/api/v1/container/<name>', methods=['DELETE'])
@api_auth()
def delete_container(name):
    try:
        lxc.destroy(name)
        return jsonify(status="ok"), 200
    except lxc.ContainerDoesntExists:
        return jsonify(status="error", error="Container doesn' t exists"), 400


@app.route('/api/v1/token/', methods=['POST'])
@api_auth()
def add_token():
    data = request.get_json(force=True)
    if data is None or 'token' not in data:
        return jsonify(status="error", error="Bad request"), 400

    if 'description' not in data:
        data.update(description="no description")
    g.db.execute('insert into api_tokens(description, token) values(?, ?)', [data['description'], data['token']])
    g.db.commit()
    return jsonify(status="ok"), 200


@app.route('/api/v1/token/<token>', methods=['DELETE'])
@api_auth()
def delete_token(token):
    g.db.execute('delete from api_tokens where token=?', [token])
    g.db.commit()
    return jsonify(status="ok"), 200


if __name__ == '__main__':
    # override debug configuration from command line
    app.debug = True if '--debug' in sys.argv[1:] else DEBUG
    if app.config['SSL']:
        from OpenSSL import SSL
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(app.config['PKEY'])
        context.use_certificate_file(app.config['CERT'])
        app.run(host=app.config['ADDRESS'], port=app.config['PORT'], ssl_context=context)
    else:
        app.run(host=app.config['ADDRESS'], port=app.config['PORT'])
