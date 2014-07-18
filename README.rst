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
  $ echo "deb http://claudyus.github.io/LXC-Web-Panel/ ./" | sudo tee /etc/apt/sources.list.d/lwp.list
  $ sudo apt-get update
  $ sudo apt-get install lwp


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

LDAP configuration
^^^^^^^^^^^^^^^^^^

To enable ldap auth you should set ``auth`` type to ``ldap`` inside your config file than configure all options inside ldap section.
See lwp.example.conf for references.

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


Hacking LWP
-----------

To develop lwp you need some extra tools.

You should install nodejs and bower to benefit from the bower package manager, you should also ensure to have lwp.conf somewhere in /etc/lwp or local direcotry and you should ensure that lwp.db exist in the configured path.

You can also rebuild gh-pages using ``make site`` but this require Cactus v3 and some other pyhton libs.

Here some shell tips:

::

  $ git clone this repo
  $ sudo apt-get install nodejs npm
  $ sudo npm install -g bower
  $ bower install #download bower packages
  Configure lwp in /etc/lwp/lwp.conf and check path for lwp.db
  $ sudo ./lwp.py --debug

If you want to rebuild gh-pages

::

  $ sudo pip install git+https://github.com/koenbok/Cactus.git@v3
  $ make site #rebuild gh-pages and debian package
  $ cd gh-pages && make serve # visit localhost:8000 for gh-pages

Before start to coding please check that you editor support editorconfig (http://editorconfig.org/).


LICENSE
-------

This work is released under MIT License