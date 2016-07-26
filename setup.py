#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'requests>=2.5',
    'websocket-client>=0.37.0',
]

setup(
    name = 'GDAX',
    version = '0.1.0',
    author = 'Daniel Paquin',
    author_email = 'dpaq34@gmail.com',
    url = 'https://github.com/danpaquin/coinbase-gdax-python',
    packages = find_packages(),
    install_requires = install_requires,
    description = 'A Python client for the GDAX API',
    download_url = 'https://github.com/danpaquin/coinbase-gdax-python/archive/master.zip',
    keywords = ['coinbase', 'gdax', 'bitcoin', 'ethereum'],
    classifiers = [],
)
