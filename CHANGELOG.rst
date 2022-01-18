2022/01/18 Version 9.0.3
------------------------

- Improve type safety of ``EventEmitter#on``, ``EventEmitter#add_listener``
  and ``EventEmitter#listens_to`` by parameterizing the ``Handler``
- Minor fixes to documentation

2022/01/17 Version 9.0.2
------------------------

- Add ``tests_require`` to setup.py, fixing COPR build
- Install as an editable package in ``environment.yml`` and
  ``requirements_docs.txt``, fixing Conda workflows and ReadTheDocs
  respectively

2022/01/17 Version 9.0.1
------------------------

- Fix regression where ``EventEmitter#listeners`` began crashing when called
  with uninitialized listeners

2022/01/17 Version 9.0.0
------------------------

Compatibility:

- Drop 3.6 support

New features:

- New ``EventEmitter.event_names()`` method (see PR #96)
- Type annotations and type checking with ``pyright``
- Exprimental ``pyee.cls`` module exposing an ``@evented`` class decorator
  and a ``@on`` method decorator (see PR #84)

Moved/deprecated interfaces:

- ``pyee.TwistedEventEmitter`` -> ``pyee.twisted.TwistedEventEmitter``
- ``pyee.AsyncIOEventEmitter`` -> ``pyee.asyncio.AsyncIOEventEmitter``
- ``pyee.ExecutorEventEmitter`` -> ``pyee.executor.ExecutorEventEmitter``
- ``pyee.TrioEventEmitter`` -> ``pyee.trio.TrioEventEmitter``

Removed interfaces:

- ``pyee.CompatEventEmitter``

Documentation fixes:

- Add docstring to ``BaseEventEmitter``
- Update docstrings to reference ``EventEmitter`` instead of ``BaseEventEmitter``
  throughout

Developer Setup & CI:

- Migrated builds from Travis to GitHub Actions
- Refactor developer setup to use a local virtualenv

2021/8/14 Version 8.2.2
-----------------------

- Correct version in docs

2021/8/14 Version 8.2.1
-----------------------

- Add .readthedocs.yaml file
- Remove vcversioner dependency from docs build


2021/8/14 Version 8.2.0
-----------------------

- Remove test_requires and setup_requires directives from setup.py (closing #82)
- Remove vcversioner from dependencies
- Streamline requirements.txt and environment.yml files
- Update and extend CONTRIBUTING.rst
- CI with GitHub Actions instead of Travis (closing #56)
- Format all code with black
- Switch default branch to ``main``
- Add the CHANGELOG to Sphinx docs (closing #51)
- Updated copyright information

2020/10/08 Version 8.1.0
------------------------
- Improve thread safety in base EventEmitter
- Documentation fix in ExecutorEventEmitter

2020/09/20 Version 8.0.1
------------------------
- Update README to reflect new API

2020/09/20 Version 8.0.0
------------------------
- Drop support for Python 2.7
- Remove CompatEventEmitter and rename BaseEventEmitter to EventEmitter
- Create an alias for BaseEventEmitter with a deprecation warning

2020/09/20 Version 7.0.4
------------------------
- setup_requires vs tests_require now correct
- tests_require updated to pass in tox
- 3.7 testing removed from tox
- 2.7 testing removed from Travis

2020/09/04 Version 7.0.3
------------------------
- Tag license as MIT in setup.py
- Update requirements and environment to pip -e the package

2020/05/12 Version 7.0.2
------------------------
- Support Python 3.8 by attempting to import TimeoutError from
  ``asyncio.exceptions``
- Add LICENSE to package manifest
- Add trio testing to tox
- Add Python 3.8 to tox
- Fix Python 2.7 in tox

2020/01/30 Version 7.0.1
------------------------
- Some tweaks to the docs

2020/01/30 Version 7.0.0
------------------------
- Added a ``TrioEventEmitter`` class for intended use with trio
- ``AsyncIOEventEmitter`` now correctly handles cancellations
- Add a new experimental ``pyee.uplift`` API for adding new functionality to
  existing event emitters

2019/04/11 Version 6.0.0
------------------------
- Added a ``BaseEventEmitter`` class which is entirely synchronous and
  intended for simple use and for subclassing
- Added an ``AsyncIOEventEmitter`` class for intended use with asyncio
- Added a ``TwistedEventEmitter`` class for intended use with twisted
- Added an ``ExecutorEventEmitter`` class which runs events in an executor
- Deprecated ``EventEmitter`` (use one of the new classes)


2017/11/18 Version 5.0.0
------------------------

- CHANGELOG.md reformatted to CHANGELOG.rst
- Added CONTRIBUTORS.rst
- The `listeners` method no longer returns the raw list of listeners, and
  instead returns a list of unwrapped listeners; This means that mutating
  listeners on the EventEmitter by mutating the list returned by
  this method isn't possible anymore, and that for once handlers this method
  returns the unwrapped handler rather than the wrapped handler
- `once` API now returns the unwrapped handler in both decorator and
  non-decorator cases
- Possible to remove once handlers with unwrapped handlers
- Internally, listeners are now stored on a OrderedDict rather than a list
- Minor stylistic tweaks to make code more pythonic

2017/11/17 Version 4.0.1
------------------------

- Fix bug in setup.py; Now publishable

2017/11/17 Version 4.0.0
------------------------

- Coroutines now work with .once
- Wrapped listener is removed prior to hook execution rather than after for
  synchronous .once handlers

2017/02/12 Version 3.0.3
------------------------

- Add universal wheel

2017/02/10 Version 3.0.2
------------------------

- EventEmitter now inherits from object

2016/10/02 Version 3.0.1
------------------------

- Fixes/Updates to pyee docs
- Uses vcversioner for managing version information

2016/10/02 Version 3.0.0
------------------------

- Errors resulting from async functions are now proxied to the "error"
  event, rather than being lost into the aether.

2016/10/01 Version 2.0.3
------------------------

- Fix setup.py broken in python 2.7
- Add link to CHANGELOG in README

2016/10/01 Version 2.0.2
------------------------

- Fix RST render warnings in README

2016/10/01 Version 2.0.1
------------------------

- Add README contents as long\_description inside setup.py

2016/10/01 Version 2.0.0
------------------------

- Drop support for pythons 3.2, 3.3 and 3.4 (support 2.7 and 3.5)
- Use pytest instead of nose
- Removed Event\_emitter alias
- Code passes flake8
- Use setuptools (no support for users without setuptools)
- Reogranized docs, hosted on readthedocs.org
- Support for scheduling coroutine functions passed to `@ee.on`

2016/02/15 Version 1.0.2
------------------------

- Make copy of event handlers array before iterating on emit

2015/09/21 Version 1.0.1
------------------------

- Change URLs to reference jfhbrook

2015/09/20 Version 1.0.0
------------------------

- Decorators return original function for `on` and `once`
- Explicit python 3 support
- Addition of legit license file
- Addition of CHANGELOG.md
- Now properly using semver
