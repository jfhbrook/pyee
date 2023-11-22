# Configuration file for the Sphinx documentation builder.

# pyee uses mkdocs for its primary documentation. However, it uses sphinx to
# generate a man page.

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import toml

with open("../pyproject.toml", "r") as f:
    pyproject_toml = toml.load(f)

project = "pyee"
copyright = "2023, Josh Holbrook"
author = "Josh Holbrook"
release = f'v{pyproject_toml["project"]["version"]}'

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "index.md"]

root_doc = "man"
