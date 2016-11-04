#!/usr/bin/env python

# Remove .egg-info directory if it exists, to avoid dependency problems with
# partially-installed packages (20160119/dphiffer)

import os, sys
from shutil import rmtree

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
egg_info = cwd + "/mapzen.whosonfirst.diff.egg-info"
if os.path.exists(egg_info):
    rmtree(egg_info)

from setuptools import setup, find_packages

packages = find_packages()
version = open("VERSION").read()
desc = open("README.md").read()

setup(
    name='mapzen.whosonfirst.diff',
    namespace_packages=['mapzen', 'mapzen.whosonfirst'],
    version=version,
    description='Python library for describing changes between versions of a Who\'s On First document',
    author='Mapzen',
    url='https://github.com/whosonfirst/py-mapzen-whosonfirst-diff',
    install_requires=[
        'mapzen.whosonfirst.utils>=0.19',
        'deepdiff',
        'geojson',
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-utils/tarball/master#egg=mapzen.whosonfirst.utils-0.19',
        ],
    packages=packages,
    scripts=[
        'scripts/wof-diff',
        ],
    download_url='https://github.com/whosonfirst/py-mapzen-whosonfirst-diff/releases/tag/' + version,
    license='BSD')
