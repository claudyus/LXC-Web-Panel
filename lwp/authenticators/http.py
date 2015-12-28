# -*- coding: utf-8 -*-
import requests

from lwp.utils import read_config_file


class http:

    """Check if ``user``/``password`` are valid."""

    def __init__(self):
        self.HTTP_USER = read_config_file().get('http', 'username')
        self.HTTP_PASSWORD = read_config_file().get('http', 'password')
        self.HTTP_AUTH_URL = read_config_file().get('http', 'auth_url')
        self.HTTP_SSL_VERIFY = read_config_file().get('http', 'ssl_verify')

    def authenticate(self, username, password):
        payload = {self.HTTP_USER: username, self.HTTP_PASSWORD: password}
        return requests.post(self.HTTP_AUTH_URL, data=payload, verify=self.HTTP_SSL_VERIFY).status_code in (200, 201)
