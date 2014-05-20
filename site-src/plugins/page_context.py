#coding:utf-8

import os


def preBuildPage(page, context, data):
    """
    Updates the context of the page to include: the page itself as {{ CURRENT_PAGE }}
    """

    # This will run for each page that Cactus renders.
    # Any changes you make to context will be passed to the template renderer for this page.

    md5 = open(os.getcwd() + '/../md5sum', 'r')
    arr = []
    for line in md5:
        parts = line.split()
        dic = {'file': parts[1], 'md5': parts[0]}
        arr.append(dic)

    extra = {
        "CURRENT_PAGE": page,
        # Add your own dynamic context elements here!
        "released_files": arr
    }

    context.update(extra)
    return context, data
