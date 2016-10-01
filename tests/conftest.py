import sys

collect_ignore = []

if sys.version_info[0] < 3 and sys.version_info[1] < 4:
    collect_ignore.append('./test_asyncio.py')
