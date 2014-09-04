LXC-Web-Panel
=============

This is a fork of the original LXC-Web-Panel from https://github.com/lxc-webpanel/LXC-Web-Panel with a lot of improvements and bug fix for LXC 1.0+.

This version of lwp is featuring backup capability, RestAPI interface, LDAP support other that the necessary fixes to work with latest lxc version.

If you use this fork please ensure to use al least lxc 1.0.4. The code was tested on Ubuntu 12.04 and 14.04.

On ubuntu 12.04 you should install:

  - LXC from this ppa: https://launchpad.net/~ubuntu-lxc/+archive/daily
  - python-flask from ppa: https://launchpad.net/~chris-lea/+archive/python-flask

Installation
------------

You can download latest debian packages from http://claudyus.github.io/LXC-Web-Panel/download.html or, better, you can also use the lwp debian repo:

::

  $ wget -O - http://claudyus.github.io/LXC-Web-Panel/claudyus.gpg.key | sudo apt-key add -
  $ echo "deb http://claudyus.github.io/LXC-Web-Panel/ debian/" | sudo tee /etc/apt/sources.list.d/lwp.list
  $ sudo apt-get update
  $ sudo apt-get install lwp

Beware: The repository system was reorganize after the 0.6 release. See `this blog post <http://claudyus.github.io/LXC-Web-Panel/posts/02-reorganize-deb-repo.html>`_ for more information

Note: you can also include the debian-testing repo inside your source.list file to receive release candidate build.

Configuration
-------------

1. Copy /etc/lwp/lwp.example.conf to /etc/lwp/lwp.conf
2. edit it
3. start lwp service ``# service lwp start``

Your lwp panel is not at http://locahost:5000/

SSL configuration
^^^^^^^^^^^^^^^^^

To add SSL Support add to global section of lwp.conf this entries:

::

 ssl = True
 pkey = mykey.key
 cert = mykey.cert


Where mykey.key and mykey.cert are the key and the certificate generated previously for example by the command:

::

 openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mykey.key -out mykey.cert

Authentication
^^^^^^^^^^^^^^

Default authentication is against the internal sqlite database, but it's possible to configure alternative backends.

LDAP
++++

To enable ldap auth you should set ``auth`` type to ``ldap`` inside your config file than configure all options inside ldap section.
See lwp.example.conf for references.

htpasswd
++++++++

To enable authentication agains htpasswd file you should set ``auth`` type to ``htpasswd`` and ``file`` variable in ``htpasswd`` section to point to the htpasswd file.

File-bucket configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

To enable `file bucket <http://claudyus.github.io/file-bucket/>`_ integration for the backup routine you shoul set to ``true`` the ``buckets`` key inside the global section of configuation file.
Than add a section ``buckets`` like this:

::

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

 bower install
 sudo ./setup.py develop
 cp lwp.example.conf lwp.conf

Now you can run lwp locally using ``sudo ./bin/lwp --debug``

Debug is just one of the available options to profile lwp you can use ``--profiling`` options, those options can also be
used against the global installation using: ``sudo lwp --debug``

Anyway ensure to stop the lwp service if any: ``sudo service lwp stop``

Info
----

This repo contains a lot of mixed up from spare forks, I like to thanks all contributors to this project.

LICENSE
-------
This work is released under MIT License
