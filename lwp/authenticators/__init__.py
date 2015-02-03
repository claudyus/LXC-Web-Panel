# -*- coding: utf-8 -*-

def get_authenticator(auth):
    module = __import__("authenticators.{}".format(auth))
    module2 = getattr(module, auth)
    class_ = getattr(module2, auth)
    return class_()
