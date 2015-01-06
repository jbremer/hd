#!/usr/bin/env python
# Copyright (C) 2015 Jurriaan Bremer.

from setuptools import setup


setup(
    name='hd',
    version='0.1',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=[
        'hd',
    ],
    scripts=[
        'bin/hd',
    ],
    url='http://jbremer.org/',
    license='GPLv3',
    description='Hexdump library and utility.',
)
