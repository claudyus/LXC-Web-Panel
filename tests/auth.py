import unittest

from mock import MagicMock

class TestAuths(unittest.TestCase):
    """
    Those tests are against the auth plugins
    """

    def test_htpasswd_passwd_auth(self):
        # FIXME the config mock is ovewrite by lwp.app load
        #       align test file to default example.conf
        #global config
        #config = MagicMock()
        #config.get('htpasswd', 'file', return_value='/var/lwp/htpasswd')
        from lwp.authenticators.htpasswd import htpasswd

        with open('/var/lwp/htpasswd', 'w') as file_pass:
            file_pass.write('user_test:L2HG274hqrFwo\n')

        h = htpasswd()
        user = h.authenticate('user_test', 'pass')
        assert user.get('username') == 'user_test'

    def test_htpasswd_passwd_auth_wrongpass(self):
        from lwp.authenticators.htpasswd import htpasswd

        with open('/var/lwp/htpasswd', 'w') as file_pass:
            file_pass.write('user_test:L2HG274hqrFwo\n')

        h = htpasswd()
        user = h.authenticate('user_test', 'wrong_pass')
        assert user == None


    def test_http(self):
        from lwp.authenticators.http import http

        h = http()
        assert h.authenticate('test', 'user')

if __name__ == '__main__':
    unittest.main()