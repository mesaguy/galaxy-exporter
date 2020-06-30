import re


from tests import TEST_ROLE, client


from galaxy_exporter import __version__


def test_role_metrics():
    response = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response.status_code == 200
    print(f'Response role metrics text:\n{response.text}')
    assert len(response.text.split('\n')) == 40

    # Validate the returned value formats and types
    assert re.search(r'ansible_galaxy_role_created{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_score{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_community_surveys{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_downloads{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_modified{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_quality_score{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_versions{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_forks{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_imported{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_open_issues{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_stars{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_watchers{instance="mesaguy.prometheus",job="galaxy"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))
    assert re.search(r'ansible_galaxy_role_version_info{version="[0-9.]*"} (\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', response.text.strip('\n'))


def test_role_metrics_equal_probe_role_metrics():
    response1 = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response1.status_code == 200
    response2 = client.get(f'/probe?module=role&target={TEST_ROLE}')
    assert response2.status_code == 200
    assert response2.text == response1.text
