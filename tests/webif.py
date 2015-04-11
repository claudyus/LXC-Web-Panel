import subprocess
import unittest
import urllib2
import shutil
import json
import ast
import os

from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app
from lwp.utils import connect_db

token = 'myrandomapites0987'

class TestApi(LiveServerTestCase):

    db = None
    type_json = {'Content-Type': 'application/json'}

    def create_app(self):
        shutil.copyfile('lwp.db', '/tmp/db.sql')
        self.db = connect_db('/tmp/db.sql')
        self.db.execute('insert into api_tokens(description, token) values(?, ?)', ['test', token])
        self.db.commit()
        app.config['DATABASE'] = '/tmp/db.sql'
        return app

    def test_00_get_containers(self):
        shutil.rmtree('/tmp/lxc/', ignore_errors=True)
        request = urllib2.Request(self.get_server_url() + '/api/v1/containers/',
            headers={'Private-Token': token})
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)
        #assert isinstance(response.read(), list)

    def test_01_put_containers(self):
        data = {'name': 'test_vm_sshd', 'template': 'sshd'}
        request = urllib2.Request(self.get_server_url() + '/api/v1/containers/', json.dumps(data),
            headers={'Private-Token': token, 'Content-Type': 'application/json' })
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)
        assert data['name'] in os.listdir('/tmp/lxc')

    def test_02_post_containers(self):
        data = {'action': 'start'}
        request = urllib2.Request(self.get_server_url() + '/api/v1/containers/test_vm_sshd', json.dumps(data),
            headers={'Private-Token': token, 'Content-Type': 'application/json'})
        request.get_method = lambda: 'POST'
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)

    def test_03_delete_containers(self):
        request = urllib2.Request(self.get_server_url() + '/api/v1/containers/test_vm_sshd',
            headers={'Private-Token': token})
        request.get_method = lambda: 'DELETE'
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)

    def test_04_post_token(self):
        data = {'token': 'test'}
        request = urllib2.Request(self.get_server_url() + '/api/v1/tokens/', json.dumps(data),
            headers={'Private-Token': token, 'Content-Type': 'application/json'})
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)

    def test_05_delete_token(self):
        request = urllib2.Request(self.get_server_url() + '/api/v1/tokens/test',
            headers={'Private-Token': token})
        request.get_method = lambda: 'DELETE'
        response = urllib2.urlopen(request)
        self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
