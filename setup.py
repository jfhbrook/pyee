# -*- coding: utf-8 -*-

from os import path
from setuptools import find_packages, setup

README_rst = path.join(path.abspath(path.dirname(__file__)), 'README.rst')

with open(README_rst, 'r') as f:
    long_description = f.read()

setup(
    name="pyee",
    vcversioner={},

    packages=find_packages(),
    tests_require=[
        'attrs == 19.3.0; python_version < "3.0"',
        'futures; python_version < "3.0"',
        'mock; python_version >= "3.6"',
        'mock == 3.0.5; python_version < "3.6"',
        'pyhamcrest == 1.10.1; python_version < "3.5"',
        'pyparsing == 2.4.7; python_version < "3.0"',
        'pytest; python_version > "3.4"',
        'pytest == 4.6.11; python_version <= "3.4"',
        'pytest-asyncio; python_version >= "3.4"',
        'pytest-trio; python_version >= "3.7"',
        'trio; python_version > "3.6"',
        'twisted',
        'zipp == 3.0.0; python_version < "3.0"'
    ],
    setup_requires=[
        'pytest-runner',
        'vcversioner'
    ],
    include_package_data=True,

    description="A port of node.js's EventEmitter to python.",
    long_description=long_description,
    author="Joshua Holbrook",
    author_email="josh.holbrook@gmail.com",
    url="https://github.com/jfhbrook/pyee",
    license="MIT",
    keywords=[
        "events", "emitter", "node.js", "node", "eventemitter",
        "event_emitter"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Other/Nonlisted Topic"
    ]
)
