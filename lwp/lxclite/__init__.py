from __future__ import absolute_import, print_function

import subprocess
import os
import time

from lwp.exceptions import ContainerDoesntExists, ContainerAlreadyExists, ContainerAlreadyRunning, ContainerNotRunning,\
    DirectoryDoesntExists, NFSDirectoryNotMounted


# LXC Python Library

# Original author: Elie Deloumeau
# The MIT License (MIT)


def _run(cmd, output=False):
    """
    To run command easier
    """
    if output:
        try:
            out = subprocess.check_output('{}'.format(cmd), shell=True, close_fds=True)
        except subprocess.CalledProcessError:
            out = False
        return out
    return subprocess.check_call('{}'.format(cmd), shell=True, close_fds=True)  # returns 0 for True


def exists(container):
    """
    Check if container exists
    """
    if container in ls():
        return True
    return False


def create(container, template='ubuntu', storage=None, xargs=None):
    """
    Create a container (without all options)
    Default template: Ubuntu
    """
    if exists(container):
        raise ContainerAlreadyExists('Container {} already created!'.format(container))

    command = 'lxc-create -n {}'.format(container)
    command += ' -t {}'.format(template)
    if storage:
        command += ' -B {}'.format(storage)
    if xargs:
        command += ' -- {}'.format(xargs)

    return _run(command)


def clone(orig=None, new=None, snapshot=False):
    """
    Clone a container (without all options)
    """
    if orig and new:
        if exists(new):
            raise ContainerAlreadyExists('Container {} already exist!'.format(new))

        if snapshot:
            command = 'lxc-clone -s {} {}'.format(orig, new)
        else:
            command = 'lxc-clone {} {}'.format(orig, new)

        return _run(command)


def info(container):
    """
    Check info from lxc-info
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exist!'.format(container))

    output = _run('lxc-info -qn {}'.format(container), output=True).splitlines()

    state = {'pid': 0}
    for val in output:
        state[val.split(':')[0].lower().strip().replace(" ", "_")] = val.split(':')[1].strip()

    return state


def lxcdir():
    return _run('lxc-config lxc.lxcpath', output=True).strip()


def ls():
    """
    List containers directory
    """
    lxc_dir = lxcdir()
    ct_list = []

    try:
        lsdir = os.listdir(lxc_dir)
        for i in lsdir:
            # ensure that we have a valid path and config file
            if os.path.isdir('{}/{}'.format(lxc_dir, i)) and os.path.isfile(('{}/{}/config'.format(lxc_dir, i))):
                ct_list.append(i)
    except OSError:
        ct_list = []
    return sorted(ct_list)


def listx():
    """
    List all containers with status (Running, Frozen or Stopped) in a dict
    Same as lxc-list or lxc-ls --fancy (0.9)
    """
    stopped = []
    frozen = []
    running = []
    status_container = {}

    outcmd = _run('lxc-ls --fancy | grep -o \'^[^-].*\' | tail -n+2', output=True).splitlines()

    for line in outcmd:
        status_container[line.split()[0]] = line.split()[1:]

    for container in ls():
        if status_container[container][0] == 'RUNNING':
            running.append(container)
        elif status_container[container][0] == 'STOPPED':
            stopped.append(container)
        elif status_container[container][0] == 'FROZEN':
            frozen.append(container)

    return {'RUNNING': running,
            'FROZEN': frozen,
            'STOPPED': stopped}


def list_status():
    """
    List all containers with status (Running, Frozen or Stopped) in a dict
    """
    containers = []

    for container in ls():
        state = info(container)['state']
        # TODO: figure out why pycharm thinks state is an int
        containers.append(dict(container=container, state=state.lower()))

    return containers


def running():
    return listx()['RUNNING']


def frozen():
    return listx()['FROZEN']


def stopped():
    return listx()['STOPPED']


def start(container):
    """
    Starts a container
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exists!'.format(container))
    if container in running():
        raise ContainerAlreadyRunning('Container {} is already running!'.format(container))
    return _run('lxc-start -dn {}'.format(container))


def stop(container):
    """
    Stops a container
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exists!'.format(container))
    if container in stopped():
        raise ContainerNotRunning('Container {} is not running!'.format(container))
    return _run('lxc-stop -n {}'.format(container))


def freeze(container):
    """
    Freezes a container
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exists!'.format(container))
    if container not in running():
        raise ContainerNotRunning('Container {} is not running!'.format(container))
    return _run('lxc-freeze -n {}'.format(container))


def unfreeze(container):
    """
    Unfreezes a container
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exists!'.format(container))
    if container not in frozen():
        raise ContainerNotRunning('Container {} is not frozen!'.format(container))
    return _run('lxc-unfreeze -n {}'.format(container))


def destroy(container):
    """
    Destroys a container
    """
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exists!'.format(container))
    return _run('lxc-destroy -n {}'.format(container))


def checkconfig():
    """
    Returns the output of lxc-checkconfig (colors cleared)
    """
    out = _run('lxc-checkconfig', output=True)
    if out:
        return out.replace('[1;32m', '').replace('[1;33m', '').replace('[0;39m', '').replace('[1;32m', '').replace('\x1b', '').replace(': ', ':').split('\n')
    return out


def cgroup(container, key, value):
    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    return _run('lxc-cgroup -n {} {} {}'.format(container, key, value))


def backup(container, sr_type='local', destination='/var/lxc-backup/'):
    """
    Backup container with tar to a storage repository (SR). E.g: localy or with nfs
    If SR is localy then the path is /var/lxc-backup/
    otherwise if SR is NFS type then we just check if the SR is mounted in host side in /mnt/lxc-backup

    Returns path/filename of the backup instances
    """
    prefix = time.strftime("%Y-%m-%d__%H-%M.tar.gz")
    filename = '{}/{}-{}'.format(destination, container, prefix)
    was_running = False

    if not exists(container):
        raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    if sr_type == 'local':
        if not os.path.isdir(destination):
            raise DirectoryDoesntExists('Directory {} does not exist !'.format(destination))
    if sr_type == 'nfs':
        if not os.path.ismount(destination):
            raise NFSDirectoryNotMounted('NFS {} is not mounted !'.format(destination))

    if info(container)['state'] == 'RUNNING':
        was_running = True
        freeze(container)

    _run('tar czf {} -C /var/lib/lxc {}'.format(filename, container))

    if was_running is True:
        unfreeze(container)

    return filename
