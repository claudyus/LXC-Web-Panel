import subprocess
import mechanize
import cookielib
import unittest
import shutil
import os

from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app
from lwp.utils import connect_db


#class TestWebBrowser(unittest.TestCase):
class TestWebBrowser(LiveServerTestCase):
    """
        These tests are made using a stateful programmatic web browsing
        and use the cookie and standard login form to operate on the lwp.
    """

    @classmethod
    def setUpClass(cls):
        # cleanup
        shutil.copyfile('lwp.db.base', '/tmp/db.sql')
        shutil.rmtree('/tmp/lxc', ignore_errors=True)
        cj = cookielib.LWPCookieJar()
        cls.br = mechanize.Browser()
        cls.br.set_cookiejar(cj)

    def create_app(self):
        app.config['DATABASE'] = '/tmp/db.sql'
        return app

    def test_00_login(self):
        """
            login with the standard admin/admin
        """
        self.client = app.test_client()
        self.client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)

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
        assert self.br.viewing_html()

        assert 'mocktest_00_lxc' in resp
        assert 'Stopped' in resp

    def test_02_start_container(self):
        """
            the container exists, start it using /action and check badge on home
        """
        self.br.open(self.get_server_url() + "/action?action=start&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()
        assert self.br.viewing_html()

        assert 'mocktest_00_lxc' in resp
        assert 'Running' in resp

    def test_03_freeze_container(self):
        """
            freeze the container using /action and check badge on home
        """
        self.br.open(self.get_server_url() + "/action?action=freeze&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()
        assert self.br.viewing_html()

        assert 'mocktest_00_lxc' in resp
        assert 'Frozen' in resp

    def test_04_unfreeze_container(self):
        """
            unfreeze container using /action and check badge on home
        """
        self.br.open(self.get_server_url() + "/action?action=unfreeze&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()
        assert self.br.viewing_html()

        assert 'mocktest_00_lxc' in resp
        assert 'Running' in resp

    def test_05_stop_container(self):
        """
            try to stop it
        """
        self.br.open(self.get_server_url() + "/action?action=stop&name=mocktest_00_lxc")

        self.br.open(self.get_server_url() + "/home")
        resp = self.br.response().read()
        assert self.br.viewing_html()

        assert 'mocktest_00_lxc' in resp
        assert 'Stopped' in resp

    def test_06_refresh_info(self):
        """
            the _refresh_info should return json object with host info
        """
        self.br.open(self.get_server_url() + '/_refresh_info')

        j_data = self.br.response().read()
        assert 'cpu' in j_data
        assert 'disk' in j_data
        assert 'uptime' in j_data

    def test_07_create_container(self):
        """
            try to create "test_created_container"
        """
        self.br.open(self.get_server_url() + "/home")

        # select create-container form and fill it
        self.br.select_form(name="create_container")
        self.br['name'] = "test_created_container"
        resp = self.br.submit()

        assert '/home'  in resp.geturl()
        assert 'mocktest_00_lxc' in resp.read()

    def test_08_create_token(self):
        """
            try to create "test_created_container"
        """
        self.br.open(self.get_server_url() + "/lwp/tokens")

        # select create-container form and fill it
        self.br.select_form(name="lwp_token")
        self.br['token'] = "mechanize_token"
        self.br['description'] = "my_token_desc"
        resp = self.br.submit()
        body = resp.read()

        assert '/lwp/tokens'  in resp.geturl()
        assert 'mechanize_token' in body
        assert 'my_token_desc' in body


if __name__ == '__main__':
    unittest.main()
