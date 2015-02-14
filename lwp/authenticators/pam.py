# -*- coding: utf-8 -*-
from lwp.utils import config

# try Debian PAM first (PyPAM)
try:
    import PAM
except ImportError:
    import pam as pam_m


class pam:
    def __init__(self):
        self.PAM_SERVICE = config.get('pam', 'service')

    def authenticate(self, username, password):
        user = None

        # try Debian PAM module (PyPAM)
        try:
            auth = PAM.pam()

            # pam callback
            def pam_conv(auth, query_list, userData):
                response = []

                for i in range(len(query_list)):
                    query, type = query_list[i]
                    if type == PAM.PAM_PROMPT_ECHO_ON:
                        val = raw_input(query)
                        response.append((val, 0))
                    elif type == PAM.PAM_PROMPT_ECHO_OFF:
                        response.append((password, 0))
                    elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                        response.append(('', 0))
                    else:
                        return None

                return response

            auth.start(self.PAM_SERVICE)
            auth.set_item(PAM.PAM_USER, username)
            auth.set_item(PAM.PAM_CONV, pam_conv)
            try:
                auth.authenticate()
                auth.acct_mgmt()

                user = {
                    'username': username,
                    'name': username,
                    'su': 'Yes'
                }
            except PAM.error:
                pass

        except NameError:
            p = pam_m
            if p.authenticate(username, password, service=self.PAM_SERVICE):
                user = {
                    'username': username,
                    'name': username,
                    'su': 'Yes'
                }

        return user
