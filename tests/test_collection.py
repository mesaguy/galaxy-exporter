from tests import client


TEST_COLLECTION = 'community.kubernetes'


def test_collection_base():
    response = client.get(f'/collection/{TEST_COLLECTION}')
    assert response.status_code == 200
    assert response.text.startswith("<html>\n    <head>\n")
    assert response.text.count(TEST_COLLECTION) == 13
