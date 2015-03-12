# -*- coding: utf-8 -*-
from lwp.utils import query_db, hash_passwd
from lwp.models import User


class database:
    def authenticate(self, username, password):
        hash_password = hash_passwd(password)
        return User.query.filter_by(username=username).authuser(password)
