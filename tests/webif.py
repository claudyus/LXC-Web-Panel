import unittest
import urllib2
from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app

class TestWebIf(LiveServerTestCase):

    render_templates = False

    def create_app(self):
        return app

    def test_server_is_up_and_running(self):
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_views(self):
        endpoints = ('/home', '/settings/lxc-net', '/about', '/lwp/users',
            '/lwp/tokens', '/action', '/_refresh_info', '/_check_version')

        for link in endpoints:
            response = urllib2.urlopen(self.get_server_url()+link)
            self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
