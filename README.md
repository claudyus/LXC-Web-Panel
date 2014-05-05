# LXC-Web-Panel

This is a fork of LXC-Web-Panel from https://github.com/lxc-webpanel/LXC-Web-Panel

Tested on Ubuntu 12.04 using lxc from daily ppa: https://launchpad.net/~ubuntu-lxc/+archive/daily

## Installation

_Deprecated!!_
```
wget https://raw2.github.com/claudyus/LXC-Web-Panel/master/tools/install.sh -O - | sudo bash
```

## Configuration

1. Copy lwp.example.conf as /etc/lwp/lwp.conf
2. edit it
3. restart lwp service

### SSL configuration
To add SSL Support add to global section of lwp.conf this entries:

ssl = True
pkey = mykey.key
cert = mykey.cert

Where mykey.key and mykey.cert are the key and the certificate generated previously for example by the command:

 openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mykey.key -out mykey.cert

## Update

```
cd /srv/lwp
sudo git pull
```
Than check the lwp.example.conf with your /etc/lwp/lwp.conf file for new options and depends.

## Remove
```
sudo rm -fr /srv/lwp
sudo rm /etc/init.d/lwp
sudo update-rc.d lwp remove

```

### Info
This repo contains a lot of mixup from various forks, see https://github.com/claudyus/LXC-Web-Panel/network for details.
