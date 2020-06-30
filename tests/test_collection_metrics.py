import re


from tests import TEST_COLLECTION, client


def test_collection_metrics():
    response = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    assert response.status_code == 200
    print(f'Response collection metrics text:\n{response.text}')

    # Validate the returned value formats and types
    assert re.search(r'ansible_galaxy_collection_created{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_community_score{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'nsible_galaxy_collection_community_surveys{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_downloads{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_modified{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_quality_score{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_version_info{version="0.11.0"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_versions{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_collection_dependencies{instance="community.kubernetes",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))

def test_collection_metrics_equal_probe_collection_metrics():
    response1 = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=collection&target={TEST_COLLECTION}')
    assert response2.status_code == 200
    assert response2.text == response1.text
