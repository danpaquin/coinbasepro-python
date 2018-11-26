#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'sortedcontainers>=1.5.9',
    'requests>=2.13.0',
    'six>=1.10.0',
    'websocket-client>=0.40.0',
    'pymongo>=3.5.1',
]

tests_require = [
    'pytest',
    'python-dateutil>=2.7.5',
    ]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cbpro',
    version='1.1.4',
    author='Daniel Paquin',
    author_email='dpaq34@gmail.com',
    license='MIT',
    url='https://github.com/danpaquin/coinbasepro-python',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    description='The unofficial Python client for the Coinbase Pro API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url='https://github.com/danpaquin/coinbasepro-python/archive/master.zip',
    keywords=['gdax', 'gdax-api', 'orderbook', 'trade', 'bitcoin', 'ethereum', 'BTC', 'ETH', 'client', 'api', 'wrapper',
              'exchange', 'crypto', 'currency', 'trading', 'trading-api', 'coinbase', 'pro', 'prime', 'coinbasepro'],
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
