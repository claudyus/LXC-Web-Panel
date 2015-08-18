import unittest

from mock import MagicMock

class TestAuths(unittest.TestCase):

    """
    Those tests are against the auth plugins
    """

    def test_http_passwd_auth(self):
        global config
        config = MagicMock()
        config.get('htpasswd', 'file', return_value='/tmp/htpasswd')

        from lwp.authenticators.htpasswd import htpasswd

        with open('/tmp/htpasswd', 'w+') as file_pass:
            file_pass.write('user_test:L2HG274hqrFwo\n')

        h = htpasswd()
        user = h.authenticate('user_test', 'pass')
        assert user.get('username') == 'user_test'

    def test_http_passwd_auth_wrongpass(self):
        global config
        config = MagicMock()
        config.get('htpasswd', 'file', return_value='/tmp/htpasswd')

        from lwp.authenticators.htpasswd import htpasswd

        with open('/tmp/htpasswd', 'w+') as file_pass:
            file_pass.write('user_test:L2HG274hqrFwo\n')

        h = htpasswd()
        user = h.authenticate('user_test', 'wrong_pass')
        assert user == None


if __name__ == '__main__':
    unittest.main()