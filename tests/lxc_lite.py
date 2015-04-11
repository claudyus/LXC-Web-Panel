import subprocess
import unittest
import shutil
import os

import lwp.lxclite as lxc

class TestLxcLite(unittest.TestCase):

    """
    Those tests are against the lxclite class
    """
    @classmethod
    def setUpClass(cls):
        shutil.rmtree('/tmp/lxc/', ignore_errors=True)

    def test_00_create(self):
        lxc.create('test00')
        assert os.path.exists('/tmp/lxc/test00')

    def test_01_clone(self):
        lxc.clone('test00', 'testclone')
        assert os.path.exists('/tmp/lxc/test00')
        assert os.path.exists('/tmp/lxc/testclone')

    def test_02_start(self):
        lxc.start('test00')

    def test_03_freeze(self):
        lxc.freeze('test00')

    def test_04_unfreeze(self):
        lxc.unfreeze('test00')

    def test_05_stop(self):
        lxc.stop('test00')

    def test_06_destroy(self):
        lxc.destroy('test00')
        assert not os.path.exists('/tmp/lxc/test00')

if __name__ == '__main__':
    unittest.main()
