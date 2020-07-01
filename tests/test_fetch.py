import time


import pytest


from galaxy_exporter.galaxy_exporter import fetch_from_url


@pytest.mark.asyncio
async def test_fetch_from_url():
    starttime = time.time()
    # Ensure fetch returns None
    assert await fetch_from_url('fail.example.org') is None
    # Ensure retries occurred for 5 seconds
    assert time.time() - starttime >= 5
