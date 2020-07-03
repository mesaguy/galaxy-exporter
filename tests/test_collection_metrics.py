import json
import os
import re


from fastapi.responses import PlainTextResponse
from prometheus_client.exposition import generate_latest
import pytest


from galaxy_exporter import __version__
import galaxy_exporter.galaxy_exporter
from galaxy_exporter.galaxy_exporter import app, update_base_metrics
from galaxy_exporter.galaxy_exporter import Collection, set_collection_metrics
import tests
from tests import TEST_COLLECTION, client


@pytest.mark.asyncio
@app.get("/test_collection/{TEST_COLLECTION}/metrics", response_class=PlainTextResponse)
async def test_collection_metrics():
    collection_file = os.path.join(os.path.dirname(tests.__file__), 'files/collection.json')
    collection = Collection(TEST_COLLECTION)
    collection.data = json.loads(open(collection_file, 'r').read())
    collection = set_collection_metrics(collection)
    return generate_latest(registry=collection.registry)


def check_collection_response(response):
    # Validate the returned value formats and types
    assert re.search(r'ansible_galaxy_collection_created'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_community_score'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_community_surveys'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_downloads'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_modified'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_quality_score'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_version_info'
                     r'{category="collection",maintainer="community",unit="kubernetes",version="[0-9.a-z]*"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_versions'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_dependencies'
                     r'{category="collection",maintainer="community",unit="kubernetes"} '
                     r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))


def test_collection_metrics_api_count_increments():
    update_base_metrics()
    count_before = galaxy_exporter.galaxy_exporter.METRICS['api_call_count']._value.get()
    response = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    print(f'Response collection metrics text:\n{response.text}')
    assert response.status_code == 200
    assert len(response.text.split('\n')) == 28
    check_collection_response(response)
    # Ensure the API count has increased by 1
    assert galaxy_exporter.galaxy_exporter.METRICS['api_call_count']._value.get() - count_before == 1


def test_collection_metrics():
    update_base_metrics()
    response = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    print(f'Response collection metrics text:\n{response.text}')
    assert response.status_code == 200
    check_collection_response(response)
    print(f'Response collection metrics text:\n{response.text}')


def test_collection_metrics_equal_probe_collection_metrics():
    update_base_metrics()
    response1 = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    print(f'Response collection metrics text:\n{response1.text}')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=collection&target={TEST_COLLECTION}')
    assert response2.status_code == 200
    assert response2.text == response1.text
    check_collection_response(response1)


def test_collection_metrics_from_cache():
    update_base_metrics()
    # Test JSON from cache. Cached JSON has 'null' for some fields
    response = client.get(f'/test_collection/{TEST_COLLECTION}/metrics')
    print(f'Response collection metrics text:\n{response.text}')
    assert response.status_code == 200
    check_collection_response(response)
