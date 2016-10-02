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
    setup_requires=['pytest-runner', 'vcversioner'],
    tests_require=['twisted'],
    include_package_data=True,

    description="A port of node.js's EventEmitter to python.",
    long_description=long_description,
    author="Joshua Holbrook",
    author_email="josh.holbrook@gmail.com",
    url="https://github.com/jfhbrook/pyee",
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
        "Topic :: Other/Nonlisted Topic"
    ]
)
