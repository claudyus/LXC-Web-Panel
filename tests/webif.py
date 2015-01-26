import unittest
import urllib2
import shutil
import json

from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app
from lwp.utils import connect_db

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
            response = urllib2.urlopen(self.get_server_url() + link)
            self.assertEqual(response.code, 200)

class TestApi(LiveServerTestCase):

    token = 'myrandomapitestoken'
    db = None

    def create_app(self):
        shutil.copyfile('lwp.db', '/tmp/db.sql')
        self.db = connect_db('/tmp/db.sql')
        self.db.execute('insert into api_tokens(description, token) values(?, ?)', ['test', self.token])
        self.db.commit()
        app.config['DATABASE'] = '/tmp/db.sql'
        return app

    def setUp(self):
        shutil.copyfile('lwp.db', '/tmp/db.sql')
        self.db = connect_db('/tmp/db.sql')
        self.db.execute('insert into api_tokens(description, token) values(?, ?)', ['test', self.token])
        self.db.commit()

    def test_get_containers(self):
        q = urllib2.Request(self.get_server_url() + '/api/v1/containers/')
        q.add_header('Private-Token', self.token)
        response = urllib2.urlopen(q)
        self.assertEqual(response.code, 200)
        #assert isinstance(response.read(), list)

    # def test_put_containers(self):
    #     data = {'name': 'test_vm_sshd', 'template': 'sshd'}
    #     q = urllib2.Request(self.get_server_url() + '/api/v1/containers/', json.dumps(data))
    #     q.add_header('Private-Token', self.token)
    #     q.get_method = lambda: 'PUT'
    #     response = urllib2.urlopen(q)
    #     self.assertEqual(response.code, 200)

    # TODO: implement apis tests

    def test_post_token(self):
        data = {'token': 'test'}
        q = urllib2.Request(self.get_server_url() + '/api/v1/tokens/', json.dumps(data))
        q.add_header('Private-Token', self.token)
        response = urllib2.urlopen(q)
        self.assertEqual(response.code, 200)

    def test_delete_token(self):
        q = urllib2.Request(self.get_server_url() + '/api/v1/tokens/test')
        q.add_header('Private-Token', self.token)
        q.get_method = lambda: 'DELETE'
        response = urllib2.urlopen(q)
        self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main()
