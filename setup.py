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
    url='https://github.com/dodo5522/solar_monitor.git',
    install_requires=requires(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'solar_monitor = solar_monitor.__main__:main'
        ]
    },
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: Japanese',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Monitoring',
    ]
)
