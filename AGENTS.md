# Agents

pyee supplies an `EventEmitter` similar to the Node.js `EventEmitter`. It also supplies subclasses for async and threaded programming in Python.

Read [DEVELOPMENT.md](DEVELOPMENT.md) for contributor rules, the AI-assisted commit marker, and how the maintainer publishes. This file is the short loop for changing the code. Trust the justfile when it disagrees with the recipe list pasted in DEVELOPMENT.md, as that list is incomplete and may be out of date.

## Package layout

The library lives in `pyee/`.

- `pyee/base.py` defines `EventEmitter`, `PyeeError`, and `PyeeException`.
- `pyee/__init__.py` re-exports `EventEmitter`, `Handler`, `PyeeError`, and `PyeeException`.
- `pyee/asyncio.py` defines `AsyncIOEventEmitter`.
- `pyee/twisted.py` defines `TwistedEventEmitter` and imports Twisted at import time.
- `pyee/executor.py` defines `ExecutorEventEmitter`.
- `pyee/trio.py` defines `TrioEventEmitter` and imports Trio at import time.
- `pyee/uplift.py` defines `uplift` and `unwrap`.
- `pyee/cls.py` defines the `evented` class decorator and the `on` decorator.
- `pyee/py.typed` marks the package as typed.

`pyproject.toml` lists `typing-extensions` as the only runtime dependency. Trio, Twisted, and their pytest plugins are in the `dev` dependency group.

## Setup and the development loop

Install `uv`, `just`, and `npm`. `just check` calls `npx`. DEVELOPMENT.md names the same prerequisites.

Create `.venv` and install dependencies with this command:

```bash
just setup
```

The `setup` recipe runs `uv sync --dev`.

`just` with no arguments is the default recipe, `just qa`. It runs `just format`, then `just check`, then `just test`, then `just lint`.

Run the pieces on their own while you work.

```bash
just format
just check
just test
just lint
```

`just format` runs Black, then isort, on `docs`, `pyee`, and `tests`. Both tools rewrite files. Formatting is checked in `just lint`.

`just check` runs `uv run npx pyright@latest`. and `uv run mypy .` `[tool.pyright]` in `pyproject.toml` includes `pyee` and `tests`. `mypy.ini` sets `exclude` to `^venv/|^docs/`.

`just test` runs `uv run pytest ./tests`. It then removes `pytest_runner-*.egg` and `tests/__pycache__`.

`just lint` runs Black and isort in check mode, then runs flake8 on `docs`, `pyee`, and `tests`, then runs `validate-pyproject` on `pyproject.toml`.

`just docs` runs `uv run mkdocs serve`. `just build-docs` runs `just mkdocs`, then `just sphinx man`.

## Tests

Pytest collects `tests/`. `pyproject.toml` sets `testpaths` to `tests` and adds `--verbose -s`.

- `tests/test_sync.py` covers the base `EventEmitter` imported from `pyee`.
- `tests/test_asyncio.py` covers `AsyncIOEventEmitter` and imports `pytest_asyncio`.
- `tests/test_twisted.py` covers `TwistedEventEmitter` and imports Twisted with no skip.
- `tests/test_executor.py` covers `ExecutorEventEmitter`.
- `tests/test_trio.py` covers `TrioEventEmitter` and imports `trio` and `pytest_trio` with no skip.
- `tests/test_uplift.py` covers `uplift` and `unwrap`.
- `tests/test_cls.py` covers `evented` and `on`.

No test file calls `pytest.importorskip`. `tests/conftest.py` ignores `test_async.py` on Python older than 3.5, and `test_trio.py` on Python older than 3.7. There is no `test_async.py`. On Python 3.12 and newer those ignores do nothing. `just install` installs Trio and Twisted from the `dev` group, which the tests import directly.

## Conventions

The public emitter classes, plus `uplift`, `unwrap`, `evented`, and `on`, use a triple-quoted docstring. The text is prose, and names sit in backticks. Examples, when present, are Markdown fences. The docstrings have no `Args`, `Returns`, or `Raises` sections. `pyee/__init__.py` holds the package docstring, including an IPython session. The other modules have no module docstring.

`pyee/base.py`, `pyee/asyncio.py`, `pyee/twisted.py`, `pyee/executor.py`, and `pyee/trio.py` set `Self = Any` and annotate `self` as `Self`. Keep that. Pyright and mypy both have to pass.

`just format` applies Black and isort. isort uses the `appnexus` profile in `pyproject.toml`. `setup.cfg` sets flake8 `max-line-length` to 88 and `extend-ignore` to `E203`. The `dev` group includes `flake8-black`.

MkDocs builds the site from docstrings. `mkdocs.yml` loads `mkdocstrings` and `include-markdown`. `docs/api.md` points mkdocstrings at `pyee`, `pyee.asyncio`, `pyee.twisted`, `pyee.executor`, `pyee.trio`, `pyee.uplift`, and `pyee.cls`. `docs/changelog.md` includes `CHANGELOG.md`. Sphinx only builds the man page. `docs/conf.py` says so, and sets `root_doc` to `man`, which is `docs/man.rst`. `.readthedocs.yaml` selects MkDocs.

`CHANGELOG.md` headings look like `## 2026/10/17 Version 15.0.0`, then bullets. DEVELOPMENT.md requires a robot emoji at the start of the commit subject and the changelog bullet when an AI assistant wrote the change, and it requires you to tell the reviewer. New contributors go in `CONTRIBUTORS.md`. The line format is in DEVELOPMENT.md. On commits, document new features in the CHANGELOG under an upcoming release, typically labeled `## xxxx.yy.zz Version x.y.z`. If no such label exists, create the label.

## Do not

Do not publish, tag, or cut a release. Do not run `just tag`, `just publish`, `uv publish`, or `git tag`. The maintainer cuts releases manually. DEVELOPMENT.md records that process for the maintainer.

Do not edit `uv.lock`, `requirements.txt`, or `requirements_dev.txt` unless the change needs a dependency change. `just compile` rewrites the two requirements files from `pyproject.toml`.
