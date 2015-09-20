# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "pyee",
    version = "1.0.1",
    packages = ["pyee"],
    description = "A port of node.js's EventEmitter to python.",
    author = "Joshua Holbrook",
    author_email = "josh.holbrook@gmail.com",
    url = "https://github.com/jfhbrook/pyee",
    keywords = ["events", "emitter", "node.js", "node", "eventemitter", "event_emitter"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Other/Nonlisted Topic"
    ],
    long_description = """\
pyee
======

pyee supplies an event_emitter object that acts similar to the `EventEmitter`
that comes with node.js.

Example
-------

::

    In [1]: from pyee import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print 'BANG BANG'
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:

Easy-peasy.

For more, visit <https://github.com/jfhbrook/pyee> .

"""
)
