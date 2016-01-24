#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages


def readme():
    try:
        os.system('pandoc -f markdown -t rst README.md -o README.rst')
        with open('README.rst', 'r') as f:
            return f.read()
    except:
        return ''


def requires():
    try:
        return [pkg.strip() for pkg in open("requirements.txt").readlines()]
    except:
        return []


setup(
    name='solar_monitor',
    version='1.4.1',
    description='Solar charge controller monitor like TS-MPPT-60',
    long_description=readme(),
    license="GPLv2",
    author='Takashi Ando',
    url='https://github.com/dodo5522/tsmppt60_monitor',
    install_requires=requires(),
    packages=find_packages(),
    test_suite='nose.collector'
)
