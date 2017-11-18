Development And Publishing:
------------

- Given you're in a virtualenv or conda environment, you can install this
  project's dependencies with `make setup`
- You can link this project to your global space with
  ``python setup.py develop``.
- Tests can be ran with ``make test``.
- Documentation can be generated locally with ``make the_docs``.
- Version off by `git tag -a {version} -m 'Version {version}'`. No prefixed v.
  Make sure you do a commit with the updated CHANGELOG as well.
- Publish with ``make package`` followed by ``make upload``.
- RTD should build automatically but can be kicked off manually by logging in
