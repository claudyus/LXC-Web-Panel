# -*- coding: utf-8 -*-
from lwp.utils import query_db, hash_passwd


class database:
    def authenticate(self, username, password):
        hash_password = hash_passwd(password)
        return query_db('select name, username, su from users where username=? and password=?', [username, hash_password], one=True)
