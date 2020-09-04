Development And Publishing:
------------

- Set up either a virtualenv or a conda env

  - if using a virtualenv, `pip install -r requirements_dev.txt` will install
    development dependencies
  - if using conda, `conda env create` in this directory will create the
    environment and `conda env update` will update.

- Tests can be ran with ``make test``.
- Documentation can be generated locally with ``make build_docs`` and served
  with ``make serve_docs``.
- Version off by ``git tag -a {version} -m 'Release {version}'``. No prefixed
  v. Make sure you do a commit with the updated CHANGELOG as well.
- Publish with ``make package`` followed by ``make upload``.
- RTD should build automatically but can be kicked off manually by logging in.
