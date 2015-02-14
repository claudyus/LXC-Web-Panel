import subprocess
import unittest
import urllib2
import shutil
import json
import os

from flask import Flask
from flask.ext.testing import LiveServerTestCase

from lwp.app import app
from lwp.utils import connect_db


class TestMockLxc(unittest.TestCase):

    """
    Those tests are against the lxc mock system under tests/mock-lxc/

    To use those tests on your machine with lxc installed you should
     add the path in your ENV before the default one:
        export PATH=`pwd`/tests/mock-lxc/:$PATH
    """

    def test_01_config(self):
        shutil.rmtree('/tmp/lxc', ignore_errors=True)
        out = subprocess.check_output('lxc-config lxc.lxcpath', shell=True, close_fds=True).strip()
        assert out == '/tmp/lxc'

    def test_02_create(self):
        subprocess.check_output('lxc-create -n lxctest', shell=True, close_fds=True).strip()
        assert 'lxctest' in os.listdir('/tmp/lxc')
        with open('/tmp/lxc/lxctest/status') as f:
            content = f.readlines()
            assert 'STOPPED' in content[0].rstrip('\n')

    def test_03_start(self):
        subprocess.check_output('lxc-start -dn lxctest', shell=True, close_fds=True).strip()
        with open('/tmp/lxc/lxctest/status') as f:
            content = f.readlines()
            assert 'RUNNING' in content[0].rstrip('\n')

    def test_04_ls(self):
        out = subprocess.check_output('lxc-ls --fancy | grep test', shell=True, close_fds=True).strip()
        assert 'lxctest' in out

    def test_05_stop(self):
        subprocess.check_output('lxc-stop -n lxctest', shell=True, close_fds=True).strip()
        with open('/tmp/lxc/lxctest/status') as f:
            content = f.readlines()
            assert 'STOPPED' in content[0].rstrip('\n')

    def test_06_destroy(self):
        subprocess.check_output('lxc-destroy -n lxctest', shell=True, close_fds=True).strip()
        assert 'lxctest' not in os.listdir('/tmp/lxc')


if __name__ == '__main__':
    unittest.main()
