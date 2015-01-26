LXC-Web-Panel
=============

.. image:: https://travis-ci.org/claudyus/LXC-Web-Panel.svg?branch=master
    :target: https://travis-ci.org/claudyus/LXC-Web-Panel

This is a fork of the original LXC-Web-Panel from https://github.com/lxc-webpanel/LXC-Web-Panel with a lot of improvements and bug fix for LXC 1.0+.

This version of lwp is featuring backup capability, RestAPI interface, LDAP support other that the necessary fixes to work with latest lxc version. This project is also available as debian package for easly installation.

If you use this fork please ensure to use al least lxc 1.0.4. The code was tested on Ubuntu 12.04 and 14.04.

On ubuntu 12.04 you should install:

  - LXC from this ppa: https://launchpad.net/~ubuntu-lxc/+archive/daily
  - python-flask from ppa: https://launchpad.net/~chris-lea/+archive/python-flask

Installation
------------

You can download latest debian packages from http://claudyus.github.io/LXC-Web-Panel/download.html or, better, you can also use the lwp debian repo:

::

  wget -O - http://claudyus.github.io/LXC-Web-Panel/claudyus.gpg.key | sudo apt-key add -
  echo "deb http://claudyus.github.io/LXC-Web-Panel/ debian/" | sudo tee /etc/apt/sources.list.d/lwp.list
  sudo apt-get update
  sudo apt-get install lwp

Note: you can also include the debian-testing repo inside your source.list file to receive release candidate build.

Configuration
-------------

1. Copy /etc/lwp/lwp.example.conf to /etc/lwp/lwp.conf
2. edit it
3. start lwp service as root ``service lwp start``

Your lwp panel is not at http://localhost:5000/

SSL configuration
^^^^^^^^^^^^^^^^^

SSL direct support was dropped after v0.6 release.

You can configure nginx as reverse proxy if you want to use SSL encryption, see `bug #34 <https://github.com/claudyus/LXC-Web-Panel/issues/34>`_ for info.


Authentication methods
^^^^^^^^^^^^^^^^^^^^^^

Default authentication is against the internal sqlite database, but it's possible to configure alternative backends.

LDAP
++++

To enable ldap auth you should set ``auth`` type to ``ldap`` inside your config file than configure all options inside ldap section.
See lwp.example.conf for references.

Pyhton LDAP need to be installed::

  apt-get install python-ldap

htpasswd
++++++++

To enable authentication against htpasswd file you should set ``auth`` type to ``htpasswd`` and ``file`` variable in ``htpasswd`` section to point to the htpasswd file.

This backend use the crypt function, here an example where ``-d`` force the use of crypt encryption when generating the htpasswd file::

  htpasswd -d -b -c /etc/lwp/httpasswd admin admin

PAM
+++

To enable authentication against PAM you should set ``auth`` type to ``pam`` and ``service`` variable in ``pam`` section.
Python PAM module needs to be installed::

  apt-get install python-pam

With default ``login`` service all valid linux users can login to lwp.
Many more options are available via PAM Configuration, see PAM docs.

File-bucket configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

To enable `file bucket <http://claudyus.github.io/file-bucket/>`_ integration for the backup routine you shoul set to ``true`` the ``buckets`` key inside the global section of configuation file.
Than add a section ``buckets`` like this::

 [global]
 .
 .
 buckets = True

 [buckets]
 buckets_host = remote_lan_ip
 buckets_port = 1234


Developers/Debug
----------------

After a fresh git clone you should download the bower component and setup the package for development purpose.

::

 fab build_assets
 sudo ./setup.py develop
 cp lwp.example.conf lwp.conf

Now you can run lwp locally using ``sudo ./bin/lwp --debug``

Debug is just one of the available options to profile lwp you can use ``--profiling`` options, those options can also be
used against the global installation using: ``sudo lwp --debug``

Anyway ensure to stop the lwp service if any: ``sudo service lwp stop``

LICENSE
-------
This work is released under MIT License, see LICENSE file.
