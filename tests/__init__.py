from fastapi.testclient import TestClient

from galaxy_exporter.galaxy_exporter import app


client = TestClient(app)
