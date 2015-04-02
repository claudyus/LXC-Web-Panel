import subprocess
import mechanize
import unittest
import shutil
import os

from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app
from lwp.utils import connect_db


class TestWebBrowser(LiveServerTestCase):
    """
        These tests are made using a stateful programmatic web browsing
        and use the cookie and standard login form to operate on the lwp.
    """

    br = mechanize.Browser()

    @classmethod
    def setUpClass(cls):
        # cleanup
        shutil.copyfile('lwp.db.base', '/tmp/db.sql')
        shutil.rmtree('/tmp/lxc')

    def create_app(self):
        app.config['DATABASE'] = '/tmp/db.sql'
        app.config['DEBUG'] = True
        return app

    def test_00_login(self):
        """
            login with the standard admin/admin
        """
        self.br.open(self.get_server_url() + "/login")
        resp = self.br.response()
        assert self.br.viewing_html()

        # select login form and fill it
        self.br.select_form(name="form-signin")
        self.br['username'] = "admin"
        self.br['password'] = "admin"
        resp = self.br.submit()

        assert '/home'  in resp.geturl()

    def test_01_home_render(self):
        """
            we are now logged in, create a container and check that
            it is displayed in home page, the stopped badge is displayed
        """
        subprocess.check_output('lxc-create -n mocktest_00_lxc', shell=True)

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()

        assert 'mocktest_00_lxc' in resp
        assert 'Stopped' in resp

    def test_02_start_container(self):
        """
            the container exists, start it usinf /action and check badge on home
        """
        self.br.open(self.get_server_url() + "/action?action=start&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()

        assert 'mocktest_00_lxc' in resp
        assert 'Running' in resp

    def test_03_stop_container(self):
        """
            try to stop it
        """
        self.br.open(self.get_server_url() + "/action?action=stop&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()

        assert 'mocktest_00_lxc' in resp
        assert 'Stopped' in resp

    def test_04_create_container(self):
        """
            try to create "test_created_container"
        """
        self.br.open(self.get_server_url() + "/home")

        # select create-container form and fill it
        self.br.select_form(name="create-container")
        self.br['name'] = "test_created_container"
        resp = self.br.submit()

        assert '/home'  in resp.geturl()
        assert 'mocktest_00_lxc' in resp.read()

    def test_05_create_token(self):
        """
            try to create "test_created_container"
        """
        self.br.open(self.get_server_url() + "/lwp/tokens")

        # select create-container form and fill it
        self.br.select_form(name="lwp-token")
        self.br['token'] = "mechanize_token"
        self.br['description'] = "my_token_desc"
        resp = self.br.submit()
        body = resp.read()

        assert '/lwp/tokens'  in resp.geturl()
        assert 'mechanize_token' in body
        assert 'my_token_desc' in body


if __name__ == '__main__':
    unittest.main()
