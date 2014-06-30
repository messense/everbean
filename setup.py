#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import everbean


with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]
    requirements = filter(lambda x: not x.startswith('--'), requirements)

setup(
    name='Everbean',
    author='Messense Lv',
    author_email='messense@icloud.com',
    version=everbean.__version__,
    description='Everbean - sync notes from book.douban.com to Evernote',
    keywords="everbean, douban, evernote, note, book",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=['nose'],
    test_suite='nose.collector',
)
