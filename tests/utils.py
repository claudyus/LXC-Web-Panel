import subprocess
import unittest
import os


class TestCmdLine(unittest.TestCase):

    """
    Those tests are against the lwp command lines
    """

    def test_01_generate_secret(self):
        assert not os.path.exists('/etc/lwp/session_secret')
        assert not os.path.exists('/etc/lwp/lwp.conf')
        subprocess.check_call('python bin/lwp --generate-session-secret', shell=True)
        assert os.path.exists('/etc/lwp/session_secret')

    def test_02_exit_if_no_config(self):
        assert not os.path.exists('/etc/lwp/lwp.conf')
        try:
            subprocess.check_call('python bin/lwp', shell=True)
        except subprocess.CalledProcessError as e:
            assert e.returncode

if __name__ == '__main__':
    unittest.main()
