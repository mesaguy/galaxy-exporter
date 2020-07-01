import json
import os
import re
import time


from fastapi.responses import PlainTextResponse
import pytest


from galaxy_exporter import __version__
from galaxy_exporter.galaxy_exporter import METRICS, app
import tests
from tests import TEST_ROLE, client


from prometheus_client.exposition import generate_latest
from galaxy_exporter.galaxy_exporter import Role, set_role_metrics


@pytest.mark.asyncio
@app.get("/test_role/{TEST_ROLE}/metrics", response_class=PlainTextResponse)
async def test_role_metrics():
    role_file = os.path.join(os.path.dirname(tests.__file__), 'files/role.json')
    jdata = json.loads(open(role_file, 'r').read())
    role = Role(TEST_ROLE)
    role.data = jdata['data']['repository']
    role = set_role_metrics(role)
    return generate_latest(registry=role.registry)


def check_role_response(response):
    # Validate the returned value formats and types
    assert re.search(r'ansible_galaxy_role_created (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_score (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_surveys (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_downloads (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_modified (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_quality_score (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_versions (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_forks (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_imported (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_open_issues (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_stars (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_watchers (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_version_info{version="[0-9.]*"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))


def test_role_metrics_equal_probe_role_metrics():
    response1 = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=role&target={TEST_ROLE}')
    assert response2.status_code == 200
    assert response2.text == response1.text
    check_role_response(response1)


def test_role_metrics():
    count_before = METRICS['api_call_count']._value.get()
    response = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response.status_code == 200
    print(f'Response role metrics text:\n{response.text}')
    assert len(response.text.split('\n')) == 40
    check_role_response(response)
    # Ensure the API count has increased by 1
    assert METRICS['api_call_count']._value.get() - count_before == 1


def test_role_metrics_from_cache():
    # Test JSON from cache. Cached JSON has 'null' for some fields
    response = client.get(f'/test_role/{TEST_ROLE}/metrics')
    assert response.status_code == 200
    check_role_response(response)


def bad_url():
    return "http://bad.url/role/test"


@pytest.mark.asyncio
async def test_role_bad_url():
    role = Role('missing.role')
    role.url = bad_url
    starttime = time.time()
    # Ensure using a bad URL returns None
    assert await role.update() is None
    # Ensure bad URL is retried for 5 seconds
    assert time.time() - starttime >= 5
