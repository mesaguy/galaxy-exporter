from tests import TEST_ROLE, client


def test_role_community_score():
    response = client.get(f'/role/{TEST_ROLE}/community_score')
    assert response.status_code == 200
    assert response.text.isdigit() or float(response.text)


def test_role_community_surveys():
    response = client.get(f'/role/{TEST_ROLE}/community_surveys')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_created():
    response = client.get(f'/role/{TEST_ROLE}/created')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_downloads():
    response = client.get(f'/role/{TEST_ROLE}/downloads')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_forks():
    response = client.get(f'/role/{TEST_ROLE}/forks')
    assert response.status_code == 200
    assert response.text.isdigit()
    assert int(response.text) > 4


def test_role_imported():
    response = client.get(f'/role/{TEST_ROLE}/imported')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_modified():
    response = client.get(f'/role/{TEST_ROLE}/modified')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_open_issues():
    response = client.get(f'/role/{TEST_ROLE}/open_issues')
    assert response.status_code == 200
    assert response.text.isdigit()


def test_role_quality_score():
    response = client.get(f'/role/{TEST_ROLE}/quality_score')
    assert response.status_code == 200
    assert response.text.isdigit() or float(response.text)


def test_role_stars():
    response = client.get(f'/role/{TEST_ROLE}/stars')
    assert response.status_code == 200
    assert response.text.isdigit()
    assert int(response.text) > 20


def test_role_version():
    response = client.get(f'/role/{TEST_ROLE}/version')
    assert response.status_code == 200


def test_role_versions():
    response = client.get(f'/role/{TEST_ROLE}/versions')
    assert response.status_code == 200
    assert response.text.isdigit()
    assert int(response.text) > 50


def test_role_watchers():
    response = client.get(f'/role/{TEST_ROLE}/watchers')
    assert response.status_code == 200
    assert response.text.isdigit()
