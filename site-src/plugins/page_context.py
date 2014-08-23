#coding:utf-8

import os
import csv

md5 = open(os.getcwd() + '/../md5sum', 'r')
arr = []
for line in md5:
    parts = line.split()
    dic = {'file': parts[1], 'md5': parts[0]}
    arr.append(dic)

with open(os.getcwd() + '/../changelog.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    #  0     1    2
    # date;hash;string
    changelog = []
    for row in csvreader:
        changelog.append({'date': row[0].split(" ")[0], 'hash': row[1], 'string': row[2],
                          'is_release': row[2].find("tag ") != -1 or row[2].find("Release ") != -1 or row[1] == '472dd67' })


def preBuildPage(page, context, data):
    """
    Updates the context of the page to include: the page itself as {{ CURRENT_PAGE }}
    """

    # This will run for each page that Cactus renders.
    # Any changes you make to context will be passed to the template renderer for this page.

    extra = {
        "CURRENT_PAGE": page,
        # Add your own dynamic context elements here!
        "released_files": arr,
        "CHANGELOG": changelog
    }

    context.update(extra)
    return context, data
