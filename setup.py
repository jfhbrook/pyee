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
        'mock',
        'pytest',
        'pytest-asyncio; python_version >= "3.4"',
        'pytest-trio; python_version >= "3.7"',
        'trio; python_version > "3.6"',
        'twisted'
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Other/Nonlisted Topic"
    ]
)
