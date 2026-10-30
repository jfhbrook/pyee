set dotenv-load := true

sphinx-sphinxbuild := "sphinx-build"
sphinx-sphinxopts := ""
sphinx-sourcedir := "docs"
sphinx-builddir := "_build"

# Format, type check, test and lint
qa:
  @just format
  @just check
  @just test
  @just lint

#
# Installing, updating and upgrading dependencies
#

# Set up the environment
setup:
  uv sync --dev

# Update dependencies
update:
  uv sync --dev --upgrade

#
# Development tooling - linting, formatting, etc
#

# Format the project
format:
  uv run black ./docs './pyee' ./tests
  uv run isort --settings-file . ./docs ./pyee ./tests

# Lint the project
lint:
  uv run black --check ./docs './pyee' ./tests
  uv run isort --settings-file . --check ./docs ./pyee ./tests
  uv run flake8 ./docs './pyee' ./tests
  uv run validate-pyproject ./pyproject.toml

# Check type annotations
check: pyright mypy

# Check type annotations with pyright
pyright:
  uv run npx pyright@latest

# Check type annotations with mypy
mypy:
  uv run mypy .

# Run tests with pytest
test:
  uv run pytest ./tests
  @just _clean-test

_clean-test:
  rm -f pytest_runner-*.egg
  rm -rf tests/__pycache__

#
# Shell and console
#

# Open a bash shell with the venv activated
shell:
  uv run bash

# Open a Jupyter console
console:
  uv run jupyter console

#
# Documentation
#

# Live generate docs and host on a development webserver
docs:
  uv run mkdocs serve

# Generate man page and open for preview
man: (sphinx 'man')
  uv run man -l _build/man/pyee.1

# Build the documentation
build-docs:
  @just mkdocs
  @just sphinx man

# Run mkdocs
mkdocs:
  uv run mkdocs build

# Run sphinx
sphinx TARGET:
	uv run {{ sphinx-sphinxbuild }} -M "{{ TARGET }}" "{{ sphinx-sourcedir }}" "{{ sphinx-builddir }}" {{ sphinx-sphinxopts }}

_clean-docs:
  rm -rf site
  rm -rf _build

#
# Package publishing
#

# Build the package
build:
  uv build

_clean-build:
  rm -rf dist

# Tag the release in git
tag:
  uv run git tag -a "v$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')" -m "Release $(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"

# Build the package and publish it to PyPI
publish:
  uv publish

# Clean up loose files
clean: _clean-test _clean-docs
  rm -rf .venv
  rm -rf pyee.egg-info
  rm -f pyee/*.pyc
  rm -rf pyee/__pycache__
