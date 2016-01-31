from __future__ import absolute_import, print_function, division

import os
import re
import time
import platform
import subprocess
import ConfigParser

from lwp.exceptions import ContainerNotExists, LxcConfigFileNotComplete
from lwp.lxclite import exists, stopped
from lwp.lxclite import lxcdir
from lwp.utils import cgroup_ext

SESSION_SECRET_FILE = '/etc/lwp/session_secret'


class FakeSection(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[DEFAULT]\n'

    def readline(self):
        if self.sechead:
            try:
                return self.sechead
            finally:
                self.sechead = None
        else:
            return self.fp.readline()


def del_section(filename=None):
    if filename:
        with open(filename, 'r') as f:
            read = f.readlines()
        i = 0
        while i < len(read):
            if '[DEFAULT]' in read[i]:
                del read[i]
                break
        with open(filename, 'w') as f:
            f.writelines(read)


def file_exist(filename):
    """
    checks if a given file exist or not
    """
    try:
        with open(filename) as f:
            f.close()
            return True
    except IOError:
        return False


def memory_usage(name):
    """
    returns memory usage in MB
    """
    if not exists(name):
        raise ContainerNotExists("The container (%s) does not exist!" % name)
    if name in stopped():
        return 0
    cmd = ['lxc-cgroup -n %s memory.usage_in_bytes' % name]
    try:
        out = subprocess.check_output(cmd, shell=True).splitlines()
    except subprocess.CalledProcessError:
        return 0
    return int(int(out[0]) / 1024 / 1024)


def host_memory_usage():
    """
    returns a dict of host memory usage values
                    {'percent': int((used/total)*100),
                    'percent_cached':int((cached/total)*100),
                    'used': int(used/1024),
                    'total': int(total/1024)}
    """
    total, free, buffers, cached = 0, 0, 0, 0
    with open('/proc/meminfo') as out:
        for line in out:
            parts = line.split()
            key = parts[0]
            value = parts[1]
            if key == 'MemTotal:':
                total = float(value)
            if key == 'MemFree:':
                free = float(value)
            if key == 'Buffers:':
                buffers = float(value)
            if key == 'Cached:':
                cached = float(value)
    used = (total - (free + buffers + cached))
    return {'percent': int((used / total) * 100),
            'percent_cached': int((cached / total) * 100),
            'used': int(used / 1024),
            'total': int(total / 1024)}


def host_cpu_percent():
    """
    returns CPU usage in percent
    """
    with open('/proc/stat', 'r') as f:
        line = f.readlines()[0]

    data = line.split()
    previdle = float(data[4])
    prevtotal = float(data[1]) + float(data[2]) + float(data[3]) + float(data[4])
    time.sleep(0.1)

    with open('/proc/stat', 'r') as f:
        line = f.readlines()[0]

    data = line.split()
    idle = float(data[4])
    total = float(data[1]) + float(data[2]) + float(data[3]) + float(data[4])
    intervaltotal = total - prevtotal
    percent = int(100 * (intervaltotal - (idle - previdle)) / intervaltotal)
    return str('%.1f' % percent)


def host_disk_usage(partition=None):
    """
    returns a dict of disk usage values
                    {'total': usage[1],
                    'used': usage[2],
                    'free': usage[3],
                    'percent': usage[4]}
    """
    partition = lxcdir()
    usage = subprocess.check_output(['df -h %s' % partition], shell=True).split('\n')[1].split()
    return {'total': usage[1],
            'used': usage[2],
            'free': usage[3],
            'percent': usage[4]}


def host_uptime():
    """
    returns a dict of the system uptime
            {'day': days,
            'time': '%d:%02d' % (hours,minutes)}
    """
    with open('/proc/uptime') as f:
        uptime = int(f.readlines()[0].split('.')[0])
    minutes = int(uptime / 60) % 60
    hours = int(uptime / 60 / 60) % 24
    days = int(uptime / 60 / 60 / 24)
    return {'day': days,
            'time': '%d:%02d' % (hours, minutes)}


def name_distro():
    """
    return the System version
    """
    dist = '%s %s - %s' % platform.linux_distribution()

    return dist


def get_templates_list():
    """
    returns a sorted lxc templates list
    """
    templates = []

    try:
        path = os.listdir('/usr/share/lxc/templates')
    except OSError:
        # TODO: if this folder doesn't exist, it will cause a crash
        path = os.listdir('/usr/lib/lxc/templates')

    if path:
        for line in path:
                templates.append(line.replace('lxc-', ''))

    return sorted(templates)


def check_version():
    """
    returns latest LWP version (dict with current)
    """
    try:
        version = subprocess.check_output('git describe --tags', shell=True)
    except subprocess.CalledProcessError:
        version = open(os.path.join(os.path.dirname(__file__), 'version')).read()[0:-1]
    return {'current': version}


def get_net_settings():
    """
    returns a dict of all known settings for LXC networking
    """
    filename = '/etc/default/lxc-net'
    if not file_exist(filename):
        filename = '/etc/default/lxc'
    if not file_exist(filename):
        raise LxcConfigFileNotComplete('Cannot find lxc-net config file! Check if /etc/default/lxc-net exists')
    config = ConfigParser.SafeConfigParser()

    config.readfp(FakeSection(open(filename)))
    cfg = {
        'use': config.get('DEFAULT', 'USE_LXC_BRIDGE').strip('"'),
        'bridge': config.get('DEFAULT', 'LXC_BRIDGE').strip('"'),
        'address': config.get('DEFAULT', 'LXC_ADDR').strip('"'),
        'netmask': config.get('DEFAULT', 'LXC_NETMASK').strip('"'),
        'network': config.get('DEFAULT', 'LXC_NETWORK').strip('"'),
        'range': config.get('DEFAULT', 'LXC_DHCP_RANGE').strip('"'),
        'max': config.get('DEFAULT', 'LXC_DHCP_MAX').strip('"')
    }

    return cfg


def get_container_settings(name, status=None):
    """
    returns a dict of all utils settings for a container
    status is optional and should be set to RUNNING to retrieve ipv4 config (if unset)
    """
    filename = '{}/{}/config'.format(lxcdir(), name)
    if not file_exist(filename):
        return False
    config = ConfigParser.SafeConfigParser()
    config.readfp(FakeSection(open(filename)))

    cfg = {}
    # for each key in cgroup_ext add value to cfg dict and initialize values
    for options in cgroup_ext.keys():
        if config.has_option('DEFAULT', cgroup_ext[options][0]):
            cfg[options] = config.get('DEFAULT', cgroup_ext[options][0])
        else:
            cfg[options] = ''  # add the key in dictionary anyway to match form

    # if ipv4 is unset try to determinate it
    if cfg['ipv4'] == '' and status == 'RUNNING':
        cmd = ['lxc-ls --fancy --fancy-format name,ipv4|grep -w \'%s\\s\' | awk \'{ print $2 }\'' % name]
        try:
            cfg['ipv4'] = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            cfg['ipv4'] = ''

    # parse memlimits to int
    cfg['memlimit'] = re.sub(r'[a-zA-Z]', '', cfg['memlimit'])
    cfg['swlimit'] = re.sub(r'[a-zA-Z]', '', cfg['swlimit'])

    return cfg


def push_net_value(key, value, filename='/etc/default/lxc-net'):
    """
    replace a var in the lxc-net config file
    """
    if filename:
        config = ConfigParser.RawConfigParser()
        config.readfp(FakeSection(open(filename)))
        if not value:
            config.remove_option('DEFAULT', key)
        else:
            config.set('DEFAULT', key, value)

        with open(filename, 'wb') as configfile:
            config.write(configfile)

        del_section(filename=filename)

        with open(filename, 'r') as load:
            read = load.readlines()

        i = 0
        while i < len(read):
            if ' = ' in read[i]:
                split = read[i].split(' = ')
                split[1] = split[1].strip('\n')
                if '\"' in split[1]:
                    read[i] = '%s=%s\n' % (split[0].upper(), split[1])
                else:
                    read[i] = '%s=\"%s\"\n' % (split[0].upper(), split[1])
            i += 1
        with open(filename, 'w') as load:
            load.writelines(read)


def push_config_value(key, value, container=None):
    """
    replace a var in a container config file
    """

    def save_cgroup_devices(filename=None):
        """
        returns multiple values (lxc.cgroup.devices.deny and lxc.cgroup.devices.allow) in a list.
        because ConfigParser cannot make this...
        """
        if filename:
            values = []
            i = 0

            with open(filename, 'r') as load:
                read = load.readlines()

            while i < len(read):
                if not read[i].startswith('#'):
                    if not (read[i] in values):
                        if re.match('lxc.cgroup.devices.deny|lxc.cgroup.devices.allow|lxc.mount.entry|lxc.cap.drop', read[i]):
                            values.append(read[i])
                i += 1
            return values

    if container:
        filename = '{}/{}/config'.format(lxcdir(), container)
        save = save_cgroup_devices(filename=filename)

        config = ConfigParser.RawConfigParser()
        config.readfp(FakeSection(open(filename)))
        if not value:
            config.remove_option('DEFAULT', key)
        elif key == cgroup_ext['memlimit'][0] or key == cgroup_ext['swlimit'][0] and value is not False:
            config.set('DEFAULT', key, '%sM' % value)
        else:
            config.set('DEFAULT', key, value)

        # Bugfix (can't duplicate keys with config parser)
        if config.has_option('DEFAULT', cgroup_ext['deny'][0]):
            config.remove_option('DEFAULT', cgroup_ext['deny'][0])
        if config.has_option('DEFAULT', cgroup_ext['allow'][0]):
            config.remove_option('DEFAULT', cgroup_ext['allow'][0])
        if config.has_option('DEFAULT', 'lxc.cap.drop'):
            config.remove_option('DEFAULT', 'lxc.cap.drop')
        if config.has_option('DEFAULT', 'lxc.mount.entry'):
            config.remove_option('DEFAULT', 'lxc.mount.entry')

        with open(filename, 'wb') as configfile:
            config.write(configfile)

        del_section(filename=filename)

        with open(filename, "a") as configfile:
            configfile.writelines(save)


def net_restart():
    """
    restarts LXC networking
    """
    cmd = ['/usr/sbin/service lxc-net restart']
    try:
        subprocess.check_call(cmd, shell=True)
        return 0
    except subprocess.CalledProcessError:
        return 1
