#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'requests>=2.5',
    'websocket-client>=0.37.0',
]

setup(
    name = 'GDAX',
    version = '0.2.0',
    author = 'Daniel Paquin',
    author_email = 'dpaq34@gmail.com',
    license='MIT',
    url = 'https://github.com/danpaquin/GDAX-Python',
    packages = find_packages(),
    install_requires = install_requires,
    description = 'The Python client for the GDAX API',
    download_url = 'https://github.com/danpaquin/GDAX-Python/archive/master.zip',
    keywords = ['coinbase', 'gdax', 'bitcoin', 'BTC', 'ETH', 'ethereum', 'client', 'api', 'wrapper', 'exchange', 'crypto', 'currency'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
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
