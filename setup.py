#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup
except ImportError:
    from distutils import setup


def readfile(file_path):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir_path, file_path), 'r') as f:
        return f.read()


setup(
    name='htmldammit',
    version='0.1.0a0',
    description=('Make every effort to properly decode HTML,'
                 ' because HTML is unicode, dammit!'),
    long_description=readfile('README.md'),
    author='Tal Einat',
    author_email='taleinat@gmail.com',
    url='https://github.com/taleinat/htmldammit',
    packages=['htmldammit'],
    package_dir={'': 'src'},
    install_requires=[
        'six',
        'beautifulsoup4',
    ],
    license='MIT',
    keywords='htmldammit HTML unicode',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
