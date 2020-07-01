import json
import os
import re


from fastapi.responses import PlainTextResponse
import pytest


from galaxy_exporter import __version__
from galaxy_exporter.galaxy_exporter import app
import tests
from tests import TEST_COLLECTION, client


from prometheus_client.exposition import generate_latest
from galaxy_exporter.galaxy_exporter import Collection, set_collection_metrics


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
    assert re.search(r'ansible_galaxy_collection_created (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_community_score (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_community_surveys (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_downloads (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_modified (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_quality_score (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_version_info{version="0.11.0"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_versions (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_dependencies (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                     response.text.strip('\n'))


def test_collection_metrics():
    response = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    assert response.status_code == 200
    check_collection_response(response)
    print(f'Response collection metrics text:\n{response.text}')


def test_collection_metrics_equal_probe_collection_metrics():
    response1 = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=collection&target={TEST_COLLECTION}')
    assert response2.status_code == 200
    assert response2.text == response1.text
    check_collection_response(response1)


def test_collection_metrics_from_cache():
    # Test JSON from cache. Cached JSON has 'null' for some fields
    response = client.get(f'/test_collection/{TEST_COLLECTION}/metrics')
    assert response.status_code == 200
    check_collection_response(response)
