import re


from tests import client


def test_role_metrics():
    response = client.get(f'/metrics')
    assert response.status_code == 200
    print(f'Response text:\n{response.text}')
    assert len(response.text.split('\n')) == 46
    assert re.search(r'process_cpu_seconds_total (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'process_open_fds (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'process_max_fds (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_exporter_api_call_count_total (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_exporter_version_info{version=\"[0-9.a-z]*\"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
