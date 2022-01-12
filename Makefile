.PHONY: setup setup-conda package upload check test tox lint format build_docs serve_docs clean

setup:
	python3 -m venv venv
	if [ -d venv ]; then . ./venv/bin/activate; fi; pip install pip wheel --upgrade
	if [ -d venv ]; then . ./venv/bin/activate; fi; pip install -r requirements.txt
	if [ -d venv ]; then . ./venv/bin/activate; fi; pip install -r requirements_dev.txt
	if [ -d venv ]; then . ./venv/bin/activate; fi; pip install -e .
	npm i

package: test lint
	if [ -d venv ]; then . ./venv/bin/activate; fi; python setup.py check
	if [ -d venv ]; then . ./venv/bin/activate; fi; python setup.py sdist
	if [ -d venv ]; then . ./venv/bin/activate; fi; python setup.py bdist_wheel --universal

upload:
	if [ -d venv ]; then . ./venv/bin/activate; fi; twine upload dist/*

check:
	if [ -d venv ]; then . ./venv/bin/activate; fi; npm run pyright

test:
	if [ -d venv ]; then . ./venv/bin/activate; fi; pytest ./tests

tox:
	if [ -d venv ]; then . ./venv/bin/activate; fi; tox

lint:
	if [ -d venv ]; then . ./venv/bin/activate; fi; flake8 ./pyee setup.py ./tests ./docs

format:
	if [ -d venv ]; then . ./venv/bin/activate; fi;  black ./pyee setup.py ./tests ./docs
	if [ -d venv ]; then . ./venv/bin/activate; fi;  isort ./pyee setup.py ./tests ./docs

build_docs:
	if [ -d venv ]; then . ./venv/bin/activate; fi; cd docs && make html

serve_docs: build_docs
	if [ -d venv ]; then . ./venv/bin/activate; fi; cd docs/_build/html && python -m http.server

clean:
	rm -rf .tox
	rm -rf dist
	rm -rf pyee.egg-info
	rm -rf pyee/*.pyc
	rm -rf pyee/__pycache__
	rm -rf pytest_runner-*.egg
	rm -rf tests/__pycache__
