#!/usr/bin/env python3

""" Install galaxy-exporter
"""

from setuptools import setup, find_packages

from galaxy_exporter import __myname__, __description__
from galaxy_exporter import __version__

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    install_requires=[
        "aiodns==2.0.0",
        "aiohttp==3.7.4",
        "async-timeout==3.0.1; python_full_version >= '3.5.3'",
        "attrs==20.3.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "cffi==1.14.5",
        "chardet==3.0.4",
        "click==7.1.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "fastapi==0.63.0",
        "h11==0.12.0; python_version >= '3.6'",
        "idna==3.1; python_version >= '3.4'",
        "multidict==5.1.0; python_version >= '3.6'",
        "prometheus-client==0.9.0",
        "pycares==4.2.0",
        "pycparser==2.20; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pydantic==1.8.1; python_full_version >= '3.6.1'",
        "python-dateutil==2.8.1",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "starlette==0.13.6; python_version >= '3.6'",
        "tenacity==7.0.0",
        "typing-extensions==3.7.4.3",
        "uvicorn==0.13.4",
        "yarl==1.6.3; python_version >= '3.6'",
    ],
    author="Mesaguy",
    author_email="mesaguy@mesaguy.com",
    name=__myname__,
    description=__description__,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://github.com/mesaguy/galaxy-exporter",
    version=__version__,
)
