from tests import client


TEST_COLLECTION = 'community.kubernetes'


def test_collection_community_score():
    response = client.get(f'/collection/{TEST_COLLECTION}/community_score')
    assert response.status_code == 200
    assert response.text.isdigit() or float(response.text)


def test_collection_community_surveys():
    response = client.get(f'/collection/{TEST_COLLECTION}/community_surveys')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_collection_created():
    response = client.get(f'/collection/{TEST_COLLECTION}/created')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_collection_dependencies():
    response = client.get(f'/collection/{TEST_COLLECTION}/dependencies')
    assert response.status_code == 200
    assert response.text.isdigit()
    assert int(response.text) == 0


def test_collection_downloads():
    response = client.get(f'/collection/{TEST_COLLECTION}/downloads')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_collection_modified():
    response = client.get(f'/collection/{TEST_COLLECTION}/modified')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_collection_quality_score():
    response = client.get(f'/collection/{TEST_COLLECTION}/quality_score')
    assert response.status_code == 200
    assert response.text.isdigit() or float(response.text)


def test_collection_version():
    response = client.get(f'/collection/{TEST_COLLECTION}/version')
    assert response.status_code == 200


def test_collection_versions():
    response = client.get(f'/collection/{TEST_COLLECTION}/versions')
    assert response.status_code == 200
    assert response.text.isdigit()
