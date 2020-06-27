from tests import client


TEST_ROLE = 'mesaguy.prometheus'


def test_role_metrics():
    response = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response.status_code == 200
