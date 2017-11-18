  - once now returns the wrapped function when called in non-decorating form
  - Minor stylistic tweaks to make code more pythonic

2017/11/17 Version 4.0.1
  - Fix bug in setup.py; Now publishable

2017/11/17 Version 4.0.0
  - Coroutines now work with .once
  - Wrapped listener is removed prior to hook execution rather than after for
    synchronous .once handlers

2017/02/12 Version 3.0.3
  - Add universal wheel

2017/02/10 Version 3.0.2
  - EventEmitter now inherits from object

2016/10/02 Version 3.0.1
  - Fixes/Updates to pyee docs
  - Uses vcversioner for managing version information

2016/10/02 Version 3.0.0
  - Errors resulting from async functions are now proxied to the "error"
    event, rather than being lost into the aether.

2016/10/01 Version 2.0.3
  - Fix setup.py broken in python 2.7
  - Add link to CHANGELOG in README

2016/10/01 Version 2.0.2
  - Fix RST render warnings in README

2016/10/01 Version 2.0.1
  - Add README contents as long\_description inside setup.py

2016/10/01 Version 2.0.0
  - Drop support for pythons 3.2, 3.3 and 3.4 (support 2.7 and 3.5)
  - Use pytest instead of nose
  - Removed Event\_emitter alias
  - Code passes flake8
  - Use setuptools (no support for users without setuptools)
  - Reogranized docs, hosted on readthedocs.org
  - Support for scheduling coroutine functions passed to `@ee.on`

2016/02/15 Version 1.0.2
  - Make copy of event handlers array before iterating on emit

2015/09/21 Version 1.0.1
  - Change URLs to reference jfhbrook

2015/09/20 Version 1.0.0
  - Decorators return original function for `on` and `once`
  - Explicit python 3 support
  - Addition of legit license file
  - Addition of CHANGELOG.md
  - Now properly using semver
