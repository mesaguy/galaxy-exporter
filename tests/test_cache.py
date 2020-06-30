import importlib
import os
import time

import galaxy_exporter.galaxy_exporter


from tests import TEST_ROLE, client


def test_cacheseconds_env_parameter(monkeypatch):
    # CACHE_SECONDS is the default
    assert galaxy_exporter.galaxy_exporter.CACHE_SECONDS == 15

    # Set the CACHE_SECONDS using str
    monkeypatch.setattr(os, 'environ', dict(CACHE_SECONDS="777"))
    importlib.reload(galaxy_exporter.galaxy_exporter)
    assert galaxy_exporter.galaxy_exporter.CACHE_SECONDS == 777

    # Set the CACHE_SECONDS using an integer
    monkeypatch.setattr(os, 'environ', dict(CACHE_SECONDS=888))
    importlib.reload(galaxy_exporter.galaxy_exporter)
    assert galaxy_exporter.galaxy_exporter.CACHE_SECONDS == 888


def test_role_metrics_cache():
    response = client.get(f'/role/{TEST_ROLE}/metrics')
    assert response.status_code == 200
    print(f'Roles: {galaxy_exporter.galaxy_exporter.ROLES}')
    assert len(galaxy_exporter.galaxy_exporter.ROLES) == 1
    role = galaxy_exporter.galaxy_exporter.ROLES[TEST_ROLE]

    # No update necessary, default CACHE_SECONDS is 15s
    assert role.needs_update() == False

    # Sleep to make testing cache expiration times possible
    time.sleep(2.1)

    # If cache expires after 1s, an update is now needed
    assert role.needs_update(cache_seconds=1) == True

    # If cache expires after 10s, an update is not needed
    assert role.needs_update(cache_seconds=10) == False
