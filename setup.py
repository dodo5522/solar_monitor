#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from setuptools import setup

setup(
    name='tsmppt60_monitor',
    version='1.3.0',
    description='TS-MPPT-60 charge controller monitor',
    author='Takashi Ando',
    url='https://github.com/dodo5522/tsmppt60_monitor',
    packages=[
        "tsmppt60_monitor",
        "tsmppt60_monitor.hook"],
    install_requires=[
        "requests>=2.6.0",
        "xively-python>=0.1.0-rc1",
        "keen",
        "tsmppt60-driver>=0.0.6"]
)
