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
