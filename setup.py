# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="pyee",
    version="2.0.0",

    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['twisted'],
    include_package_data=True,

    description="A port of node.js's EventEmitter to python.",
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
