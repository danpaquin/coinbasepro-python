#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'requests>=2.5',
    'websocket-client>=0.37.0',
]

setup(
    name = 'GDAX',
    version = '0.1.1b2',
    author = 'Daniel Paquin',
    author_email = 'dpaq34@gmail.com',
    license='MIT',
    url = 'https://github.com/danpaquin/coinbase-gdax-python',
    packages = find_packages(),
    install_requires = install_requires,
    description = 'A Python client for the GDAX API',
    download_url = 'https://github.com/danpaquin/coinbase-gdax-python/archive/master.zip',
    keywords = ['coinbase', 'gdax', 'bitcoin', 'ethereum', 'client', 'api', 'exchange', 'crypto', 'currency'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
