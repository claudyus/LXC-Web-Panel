#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'lwp/version')).read()

setup(
    name='lwp',
    version=VERSION,
    description='LXC Web Panel',
    long_description=README,
    author='Claudio Mignanti',
    author_email='c.mignanti@gmail.com',
    url='https://github.com/claudyus/LXC-Web-Panel',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask>=0.10',
        'jinja2>=2.7.2',
        'python-ldap',
        'PyOpenSSL',
    ],
    scripts=['bin/lwp'],
)
