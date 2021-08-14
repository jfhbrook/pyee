# -*- coding: utf-8 -*-

from sys import version_info as v

collect_ignore = []

if not (v[0] >= 3 and v[1] >= 5):
    collect_ignore.append("test_async.py")

if not (v[0] >= 3 and v[1] >= 7):
    collect_ignore.append("test_trio.py")
