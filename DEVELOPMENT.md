# Development And Publishing

## Prerequisites

- Python 3.10+ - either system python3 or conda
- npm - namely `npx`
- [just](https://github.com/casey/just)

## Environment Setup

To set everything up, run:

```bash
just install
```

This will create a virtualenv at `./venv` and install dependencies with pip and
pip-tools.

## Just Tasks

To list all Just tasks, run `just --list`:

```
Available recipes:
    build         # Build the package
    build-docs    # Build the documentation
    check         # Check type annotations with pyright
    clean         # Clean up loose files
    compile       # Generate locked requirements files based on dependencies in pyproject.toml
    console       # Open a Jupyter console
    default       # By default, run checks and tests, then format and lint
    docs          # Live generate docs and host on a development webserver
    format        # Format with black and isort
    install       # Install all dependencies
    lint          # Lint with flake8
    man           # Generate man page and open for preview
    mkdocs        # Run mkdocs
    publish       # Build the package and publish it to PyPI
    shell         # Open a bash shell with the venv activated
    sphinx TARGET # Run sphinx
    tag           # Tag the release in git
    test          # Run tests with pytest
    tox           # Run tests using tox
    update        # Update all dependencies
    upgrade       # Update all dependencies and rebuild the environment
    upload        # Upload built packages
```

### Updating Modules

To update the modules being used, run:

```bash
just update
```

Alternately, run everything with the just tasks, which source the activate
script before running commands. You can get a full list with `just --list`.

### conda

The author doesn't currently use Conda on any machines, and is unsupported.
Howeer, an `environment.yml` *is* provided, and is intended to manage a Conda
environment named `pyee`. These notes are a guide to how Conda *could* be
used, and for anybody who wants to add Conda support to the `justfile`.

In general, `conda env create`, `conda activate pyee` and `conda env update`
should work as far as Conda is concerned. However, you'll need to use lower
level commands to update the requirements files with pip-tools.

Instead of running `just install`, run:

```bash
just compile  # generate requirements files
conda env install  # or conda env update
```

Instead of running `just update`, run:

```bash
just clean  # removes existing requirements files
just compile
conda env update
```

Note that the other just tasks assume an activate script at `./venv/bin/activate`.
For now, you could probably stub it so that it calls `conda activate pyee`.
Supporting it would probably look like generating that script in the
venv setup task.

Finally, be cautioned that, in the past, dependencies with compiled components
were installed with Conda, such that pip left them alone after finding they
were the same version. The reason for this is that source builds will have
issues linking to non-Conda libraries. Now that it's a few years later,
however, those modules may install binary wheels and be just fine.

Either way, there's a decent shot a module with compiled components will have issues
and need to be added to `environment.yml`. In the past, I manually kept the
version matching `requirements_dev.txt`, but now that this is being generated
by pip-tools - with locks for transient dependencies - this
sort of bookkeeping is a lot harder. One option is to write a script that
will naively grep versions from the requirements file, though keep in mind
that pip versions aren't fully compatible with Conda versions. Another is
to find the conda package for the binary dependency, and install that so the
linter works. A final option is to punch Conda's linker - I've done this in
the past, but it's pretty fragile and hopefully unnecessary.

## Interactive Environments

To activate the venv in a subshell:

```bash
just shell
```

To fire up an interactive console:

```bash
just console
```

Note that I haven't figured out how to auto-exec code on load - you'll need
to import everything. The easiest thing may be to use full fat Jupyter,
potentially with [jpterm](https://github.com/davidbrochart/jpterm).


## Development Loop

There are four main just tasks:

- `just format` - format with black and isort
- `just check` - check type annotations with pyright
- `just test` - run tests with pytest
- `just lint` - lint with flake8 and validate-pyproject

To run all four in a row, simply run `just`. Then, run individual checks until
you're happy with it, and run `just` again to make sure all is well.

### Cross-Version Tests with tox

I usually lean on github actions for checking the test matrix, but `just tox`
should run them with tox. An avenue to explore may be acting smarter about
installing versions of python listed in the test matrix.

## Generating Docs

Docs for published projects are automatically generated by readthedocs, but
you can also preview them locally by running:

```bash
just docs
```

This will use `mkdoc`'s dev server - click the link, good to go. It even
supports hot reload!
  

## Publishing

### Do a Final Check

Run `just` to do final checks.

### Update the Changelog

Update the CHANGELOG.md file to detail the changes being rolled into the new
version.

### Update the Version in pyproject.toml

I do my best to follow [semver](https://semver.org) when updating versions.

### Add a Git Tag

I try to use git tags to tag versions - there's a just task:

```bash
just tag
```

### Push the Tag to GitHub

```bash
git push origin main --tags
```

### Check on GitHub Actions

This should trigger a GitHub Action which publishes to PyPI and creates a
GitHub Release. Go to GitHub and make sure it worked.

### Check on RTD

RTD should build automatically but I find there's a delay so I like to kick it
off manually. Log into [RTD](https://readthedocs.org), log in, then go
to [the pyee project page](https://readthedocs.org/projects/pyee/) and build
latest and stable.


### (Optional) Announce on Twitter

It's not official, but I like to announce the release on Twitter.


### (Optional) Build and Publish Manually

If you want to publish the package manually, run:

```bash
just publish
```

This should automatically build the package and upload with twine. However,
you can also build the package manually with `just build`, or upload the
existing build with `just upload`.


