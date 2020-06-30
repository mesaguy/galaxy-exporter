from fastapi.testclient import TestClient

from galaxy_exporter.galaxy_exporter import app


TEST_COLLECTION = 'community.kubernetes'
TEST_ROLE = 'mesaguy.prometheus'


client = TestClient(app)
