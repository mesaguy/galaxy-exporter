from tests import client


TEST_COLLECTION = 'community.kubernetes'


def test_collection_metrics():
    response = client.get(f'/collection/{TEST_COLLECTION}/metrics')
    assert response.status_code == 200
