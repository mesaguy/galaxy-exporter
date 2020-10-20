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
        "aiohttp<4,==3.6.2",
        "appdirs==1.4.4",
        "async-timeout==3.0.1; python_full_version >= '3.5.3'",
        "attrs==20.2.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "black==19.10b0; python_version >= '3.6'",
        "cached-property==1.5.2",
        "cerberus==1.3.2",
        "certifi==2020.6.20",
        "cffi==1.14.3",
        "chardet==3.0.4",
        "click==7.1.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "colorama==0.4.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "distlib==0.3.1",
        "fastapi==0.61.1",
        "h11==0.11.0",
        "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "multidict==4.7.6; python_version >= '3.5'",
        "orderedmultidict==1.0.1",
        "packaging==20.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pathspec==0.8.0",
        "pep517==0.9.1",
        "pip-shims==0.5.3; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "pipenv-setup==3.1.1",
        "pipfile==0.0.2",
        "plette[validation]==0.2.3; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "prometheus-client==0.8.0",
        "pycares==3.1.1",
        "pycparser==2.20; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pydantic==1.6.1; python_version >= '3.6'",
        "pyparsing==2.4.7; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dateutil==2.8.1",
        "regex==2020.10.15",
        "requests==2.24.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "requirementslib==1.5.13; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "starlette==0.13.6; python_version >= '3.6'",
        "tenacity==6.2.0",
        "toml==0.10.1",
        "tomlkit==0.7.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "typed-ast==1.4.1",
        "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
        "uvicorn==0.12.1",
        "vistir==0.5.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "wheel==0.35.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "yarl==1.6.2; python_version >= '3.6'",
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
