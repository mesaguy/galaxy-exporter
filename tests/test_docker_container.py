import pytest
from galaxy_exporter import __version__


from tests import galaxy_exporter_container
from tests import galaxy_exporter_client
from tests import galaxy_exporter_image
from tests import host


ROOT_HTML = """<html>
    <head>
        <title>Ansible Galaxy Exporter v%s statistics index</title>
    </head>
    <body>
        <h1>Usage</h1>
        <p>
            <a href="/metrics">Prometheus exporter process metrics</a>
        </p>
        <p>
        All role and collection names must be in the format for AUTHOR.ROLE or AUTHOR.COLLECTION
        </p>
        <p>
            Go to /role/ROLE_NAME/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/ROLE_NAME/community_score for a raw community score count</li>
                <li>/role/ROLE_NAME/community_surveys for a raw community survey count</li>
                <li>/role/ROLE_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/ROLE_NAME/downloads for a raw download count</li>
                <li>/role/ROLE_NAME/forks for a raw forks count</li>
                <li>/role/ROLE_NAME/imported for a raw imported datetime in epoch format</li>
                <li>/role/ROLE_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/ROLE_NAME/open_issues for a raw open issues count</li>
                <li>/role/ROLE_NAME/quality_score for a raw quality score count</li>
                <li>/role/ROLE_NAME/stars for a raw stars count</li>
                <li>/role/ROLE_NAME/version for a raw version number</li>
                <li>/role/ROLE_NAME/versions for a raw version count</li>
                <li>/role/ROLE_NAME/watchers for a raw watcher count</li>
            </ul>
        </p>
        <p>
            Go to /role/COLLECTION_NAME/metrics for Prometheus Metrics
        </p>
        <p>
            For simple metrics, go to:
            <ul>
                <li>/role/COLLECTION_NAME/community_score for a raw community score count</li>
                <li>/role/COLLECTION_NAME/community_surveys for a raw community survey count</li>
                <li>/role/COLLECTION_NAME/created for a raw created datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/dependencies for a raw dependency count</li>
                <li>/role/COLLECTION_NAME/downloads for a raw download count</li>
                <li>/role/COLLECTION_NAME/modified for a raw modified datetime in epoch format</li>
                <li>/role/COLLECTION_NAME/quality_score for a raw quality score count</li>
                <li>/role/COLLECTION_NAME/version for a raw version number</li>
                <li>/role/COLLECTION_NAME/versions for a raw version count</li>
            </ul>
        </p>
    </body>
</html>
""" % __version__


def test_container_starts(galaxy_exporter_container):
    assert galaxy_exporter_container.status == "running"


def test_galaxy_exporter_process_running(host):
    assert len(host.process.filter(user="nobody", comm="uvicorn")) == 1
    print(host.socket.get_listening_sockets())
    assert host.socket("tcp://0.0.0.0:9654").is_listening


def test_api_server(galaxy_exporter_client):
    galaxy_exporter_client.request('GET', '/')
    response = galaxy_exporter_client.getresponse()
    assert response.status == 200
    assert response.read() == ROOT_HTML.encode('utf-8')
