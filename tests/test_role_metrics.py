import json
import os
import re
import time


from fastapi.responses import PlainTextResponse
from prometheus_client.exposition import generate_latest
import pytest


from galaxy_exporter import __version__
import galaxy_exporter.galaxy_exporter
from galaxy_exporter.galaxy_exporter import app, update_base_metrics
from galaxy_exporter.galaxy_exporter import Role, set_role_metrics
import tests
from tests import TEST_ROLE, client


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
    assert re.search(r'ansible_galaxy_role_created'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_score'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_surveys'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_downloads'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_modified'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_quality_score'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_versions'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_forks'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_imported'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_open_issues'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_stars'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_watchers'
                     r'{category="role",maintainer="mesaguy",unit="prometheus"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_version_info'
                     r'{category="role",maintainer="mesaguy",unit="prometheus",version="[0-9.]*"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))


def test_role_metrics_equal_probe_role_metrics():
    update_base_metrics()
    response1 = client.get(f'/role/{TEST_ROLE}/metrics')
    print(f'Response role metrics text:\n{response1.text}')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=role&target={TEST_ROLE}')
    assert response2.status_code == 200
    assert response2.text == response1.text
    check_role_response(response1)


def test_role_metrics_api_count_increments():
    update_base_metrics()
    count_before = galaxy_exporter.galaxy_exporter.METRICS['api_call_count']._value.get()
    response = client.get(f'/role/{TEST_ROLE}/metrics')
    print(f'Response role metrics text:\n{response.text}')
    assert response.status_code == 200
    assert len(response.text.split('\n')) == 40
    check_role_response(response)
    # Ensure the API count has increased by 1
    assert galaxy_exporter.galaxy_exporter.METRICS['api_call_count']._value.get() - count_before == 1


def test_role_metrics_from_cache():
    update_base_metrics()
    # Test JSON from cache. Cached JSON has 'null' for some fields
    response = client.get(f'/test_role/{TEST_ROLE}/metrics')
    print(f'Response role metrics text:\n{response.text}')
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
