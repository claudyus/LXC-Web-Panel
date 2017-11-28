LXC-Web-Panel
=============

.. image:: https://travis-ci.org/claudyus/LXC-Web-Panel.svg?branch=master
    :target: https://travis-ci.org/claudyus/LXC-Web-Panel

This is a fork of the original LXC-Web-Panel from https://github.com/lxc-webpanel/LXC-Web-Panel with a lot of improvements and bug fixes for LXC 1.0+.

This version of lwp features backup capability, RestAPI interface, LDAP support, and other necessary fixes to work with the latest lxc version. This project is also available as debian package for easy installation.

If you use this fork please ensure to use at least lxc 1.0.4. The code was tested on Ubuntu 12.04 and 14.04.

On ubuntu 12.04 you should install:

  - LXC from this ppa: https://launchpad.net/~ubuntu-lxc/+archive/daily
  - python-flask from ppa: https://launchpad.net/~chris-lea/+archive/python-flask

Installation on deb based system
------------------------------------

The latest debian packages are released using packagecloud.io service since version 0.9, please update your repo config.
The install script can be found at https://packagecloud.io/claudyus/LXC-Web-Panel/install

Installation of the package can be done typing::

  sudo apt-get install lwp

Version released before 0.9 can be downloaded at http://claudyus.github.io/LXC-Web-Panel/download.html


Installation on rpm system or from source code
----------------------------------------------

If you want to run lwp from source code or in a rpm based system like Fedora you can follow the steps below.

On a fedora system you should install these deps.

::

  sudo yum update
  sudo yum install lxc lxc-devel lxc-libs lxc-extra lxc-templates python-pam python-flask fabric pytz npm

Now you should download the source code and inside the source code directory run these steps below

::

  fab build_assets         # build assets using python-fabric
  ./setup.py develop       # install python package
  mkdir -p /etc/lwp        # create config/var dirs and popolate it
  mkdir -p /var/lwp
  cp lwp.example.conf /etc/lwp/lwp.conf
  cp lwp.db /var/lwp/lwp.db
  service firewalld stop   # for fedora
  service lxc start        # if service lxc exists
  ./bin/lwp --debug        # run lwp wth debug support


Configuration
-------------

1. Copy /etc/lwp/lwp.example.conf to /etc/lwp/lwp.conf
2. edit it
3. start lwp service as root ``service lwp start``

Your lwp panel is now at http://localhost:5000/ and default username and password are admin/admin.

SSL configuration
^^^^^^^^^^^^^^^^^

SSL direct support was dropped after v0.6 release.

You can configure nginx as reverse proxy if you want to use SSL encryption, see `bug #34 <https://github.com/claudyus/LXC-Web-Panel/issues/34>`_ for info.


Authentication methods
^^^^^^^^^^^^^^^^^^^^^^

Default authentication is against the internal sqlite database, but it's possible to configure alternative backends.

LDAP
++++

To enable ldap auth you should set ``auth`` type to ``ldap`` inside your config file then configure all options inside ldap section.
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

or

::

  pip install pam

or

::

  yum install python-pam

With default ``login`` service all valid linux users can login to lwp.
Many more options are available via PAM Configuration, see PAM docs.

HTTP
+++++

This auth method is used to authenticate the users using an external http server through a POST request. To enable this method  ``auth`` type to ``http`` and configure the option under ``http`` section.

Custom autenticators
++++++++++++++++++++

If you want to use different type of authentication, create appropriate file in ``authenticators/`` directory with specific structure (example can be viewed in ``stub`` authenticator)

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

To run test locally unsure that mock-lxc scripts are in PATH (``export PATH=`pwd`/tests/mock-lxc:$PATH``) than run ``fab dev_test``

To build a local debian package run ``fab debian``

LICENSE
-------
This work is released under MIT License, see LICENSE file.
