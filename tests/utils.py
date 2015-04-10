import subprocess
import unittest
import os


class TestCmdLine(unittest.TestCase):

    """
    Those tests are against the lwp command lines
    """

    def test_generate_secret(self):
        assert not os.path.exists('/etc/lwp/session_secret')
        subprocess.check_output('python bin/lwp --generate-session-secret', shell=True)
        assert os.path.exists('/etc/lwp/session_secret')


if __name__ == '__main__':
    unittest.main()
