# -*- coding: utf-8 -*-

import simple_ci
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md', 'r') as f:
    readme = f.read()

with open('CHANGES.md', 'r') as f:
    history = f.read()


setup(
    name='simple_ci',

    description='very simple continuous integration server, supporting bitbucket.org and github.com webhooks. ',
    long_description=readme + '\n\n' + history,

    url='https://github.com/jatsz/simple_ci',
    download_url='https://github.com/jatsz/simple_ci/tarball/master',

    version=simple_ci.__version__,
    license=simple_ci.__license__,

    author=simple_ci.__author__,
    author_email='imjatsz@gmail.com',

    packages=['simple_ci'],

    classifiers=[],

    keywords = "ci",

)