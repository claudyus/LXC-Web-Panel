# -*- coding: utf-8 -*-
import sys
import hmac
import crypt

from lwp.utils import read_config_file


class htpasswd:
    def __init__(self):
        self.HTPASSWD_FILE = read_config_file().get('htpasswd', 'file')

    def authenticate(self, username, password):
        user = None
        if self.check_htpasswd(self.HTPASSWD_FILE, username, password):
            user = {
                'username': username,
                'name': username,
                'su': 'Yes'
            }

        return user

    def check_htpasswd(self, htpasswd_file, username, password):
        htuser = None

        lines = open(htpasswd_file, 'r').readlines()
        for line in lines:
            htuser, htpasswd = line.split(':')
            htpasswd = htpasswd.rstrip('\n')
            if username == htuser:
                break

        if htuser is None:
            return False
        else:
            if sys.version_info < (2, 7, 7):
                return crypt.crypt(password, htpasswd) == htpasswd
            else:
                return hmac.compare_digest(crypt.crypt(password, htpasswd), htpasswd)
