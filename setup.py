#!/usr/bin/env python3

""" Install galaxy-exporter
"""

from setuptools import setup, find_packages

from galaxy_exporter import __myname__, __description__
from galaxy_exporter import __version__

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    author='Mesaguy',
    author_email='mesaguy@mesaguy.com',
    name=__myname__,
    description=__description__,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        # Improves aiohttp performance
        'aiodns >= 2.0.0,<3',
        # For API calls to Ansible Galaxy
        'aiohttp >= 3.6.2,<4',
        'fastapi >= 0.60.1,<1',
        # For exporting Prometheus metrics
        'prometheus_client >= 0.8.0,<1',
        'python-dateutil >= 2.8.1',
        'tenacity >= 6.2.0,<7',
        'uvicorn >= 0.11.7,<1',
        ],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    extras_require={
        'testing': [
            # Codecov
            'coverage >= 5.2,<6',
            'codecov >= 2.1.8<3',
            # Testing
            'mypy >= 0.782,<1',
            'pylint >= 2.5.3,<2.6',
            'pytest >= 5.4.3,<6',
            'pytest-asyncio >= 0.11.0,<1',
            'pytest-cov >= 2.10.0,<3',
            'pytest-pep8 >= 1.0.6,<2',
            'pytest-pylint >= 0.17.0',
            'requests >= 2.24.0,<3',
        ]
    },
    url='https://github.com/mesaguy/galaxy-exporter',
    version=__version__,
)
