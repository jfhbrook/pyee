from distutils.core import setup

setup(
    name = "pyee",
    version = "0.0.7",
    packages = ["pyee"],
    description = "A port of node.js's EventEmitter to python.",
    author = "Joshua Holbrook",
    author_email = "josh.holbrook@gmail.com",
    url = "https://github.com/jesusabdullah/pyee",
    keywords = ["events", "emitter", "node.js"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7", #only one tested
        "Topic :: Other/Nonlisted Topic"
    ],
    long_description = """\
pyee
======

pyee supplies an event_emitter object that acts similar to the `EventEmitter`
that comes with node.js.

Example:
--------

::

    In [1]: from pyee import Event_emitter

    In [2]: ee = Event_emitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print 'BANG BANG'
       ...:     

    In [4]: ee.emit('event')
    BANG BANG

    In [5]: 

Easy-peasy.

For more, visit <https://github.com/jesusabdullah/pyee> .
    """
)
