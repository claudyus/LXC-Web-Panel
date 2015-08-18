# -*- coding: utf-8 -*-

from lwp.utils import read_config_file

import ldap as ldap_m


class ldap:
    def __init__(self):
        config = read_config_file()
        self.LDAP_HOST = config.get('ldap', 'host')
        self.LDAP_PORT = int(config.get('ldap', 'port'))
        self.LDAP_PROTO = 'ldaps' if config.getboolean('ldap', 'ssl') else 'ldap'
        self.LDAP_BIND_METHOD = config.get('ldap', 'bind_method')
        self.LDAP_BASE = config.get('ldap', 'base')
        self.LDAP_BIND_DN = config.get('ldap', 'bind_dn')
        self.LDAP_PASS = config.get('ldap', 'password')
        self.ID_MAPPING = config.get('ldap', 'id_mapping')
        self.DISPLAY_MAPPING = config.get('ldap', 'display_mapping')
        self.OBJECT_CLASS = config.get('ldap', 'object_class')
        self.REQUIRED_GROUP = config.get('ldap', 'required_group')

    def authenticate(self, username, password):
        user = None
        try:
            l = ldap_m.initialize("{}://{}:{}".format(self.LDAP_PROTO, self.LDAP_HOST, self.LDAP_PORT))
            l.set_option(ldap_m.OPT_REFERRALS, 0)
            l.protocol_version = 3
            if self.LDAP_BIND_METHOD == 'user':
                l.simple_bind(self.LDAP_BIND_DN, self.LDAP_PASS)
            else:
                l.simple_bind()
            attrs = ['memberOf', self.ID_MAPPING, self.DISPLAY_MAPPING] if self.REQUIRED_GROUP else []
            q = l.search_s(self.LDAP_BASE, ldap_m.SCOPE_SUBTREE, "(&(objectClass={})({}={}))".format(self.OBJECT_CLASS, self.ID_MAPPING, username), attrs)[0]
            is_member = False
            if 'memberOf' in q[1]:
                for group in q[1]['memberOf']:
                    if group.find("cn={},".format(self.REQUIRED_GROUP)) >= 0:
                        is_member = True
                        break
            if is_member is True or not self.REQUIRED_GROUP:
                l.bind_s(q[0], password, ldap_m.AUTH_SIMPLE)
                # set the parameters for user by ldap objectClass
                user = {
                    'username': q[1][self.ID_MAPPING][0].decode('utf8'),
                    'name': q[1][self.DISPLAY_MAPPING][0].decode('utf8'),
                    'su': 'Yes'
                }
        except Exception, e:
            print(str(e))

        return user
