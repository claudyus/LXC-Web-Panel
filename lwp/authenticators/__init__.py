# -*- coding: utf-8 -*-


def get_authenticator(auth):
    n = "{}.{}".format(__name__, auth)
    module = __import__(n, fromlist=[__name__])
    class_ = getattr(module, auth)
    return class_()
