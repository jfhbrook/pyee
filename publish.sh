#!/bin/bash

# I will always have to look these up, so why not just do it here?
# Ref: http://diveintopython3.org/packaging.html

python setup.py check
python setup.py sdist
python setup.py register sdist upload
