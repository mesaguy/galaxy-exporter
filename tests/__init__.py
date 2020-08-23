from http.client import HTTPConnection
import pytest
from pytest_docker_tools import build, container
import testinfra
from fastapi.testclient import TestClient


from galaxy_exporter.galaxy_exporter import app


TEST_COLLECTION = 'community.kubernetes'
TEST_ROLE = 'mesaguy.prometheus'


client = TestClient(app)


galaxy_exporter_image = build(
    nocache=False,
    scope='session',
    path='.',
)


galaxy_exporter_container = container(
    image='{galaxy_exporter_image.id}',
    scope='session',
    ports={
        '9654/tcp': None,
    }
)


@pytest.fixture(scope='session')
def galaxy_exporter_client(galaxy_exporter_container):
    port = galaxy_exporter_container.ports['9654/tcp'][0]
    return HTTPConnection(f'localhost:{port}')


@pytest.fixture(scope='session')
def host(galaxy_exporter_container, request):
    yield testinfra.get_host("docker://" + galaxy_exporter_container.id)
