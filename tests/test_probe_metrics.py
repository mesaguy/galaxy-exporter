from tests import client


def test_probe_invalid_module():
    response = client.get(f'/probe?module=test&target=test.test')
    assert response.status_code == 404
    assert response.text == '{"detail":"Unknown module test, use ' \
        '\\"collection\\" or \\"role\\""}'
