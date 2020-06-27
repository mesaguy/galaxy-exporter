from tests import client


def test_base():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text.startswith("<html>\n    <head>\n")
