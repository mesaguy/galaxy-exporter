from tests import TEST_ROLE, client


def test_role_base():
    response = client.get(f'/role/{TEST_ROLE}')
    assert response.status_code == 200
    assert response.text.startswith("<html>\n    <head>\n")
    assert response.text.count(TEST_ROLE) == 17
