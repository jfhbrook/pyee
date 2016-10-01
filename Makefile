publish:
	# I will always have to look these up, so why not just do it here?
	# Ref: http://diveintopython3.org/packaging.html
	cp README.rst README
	python setup.py check
	python setup.py sdist
	python setup.py register sdist upload

test:
	tox

lint:
	python setup.py flake8

the_docs:
	python setup.py build_sphinx
