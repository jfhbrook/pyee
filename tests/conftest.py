collect_ignore = []

try:
    import asyncio
except ImportError:
    collect_ignore.append('test_asyncio.py')
