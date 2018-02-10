# -*- coding: utf-8 -*-

from sys import version_info as v

collect_ignore = []

if not v[0] >= 3:
    collect_ignore.append('test_executor.py')
    if not v[1] >= 5:
        collect_ignore.append('test_async.py')
