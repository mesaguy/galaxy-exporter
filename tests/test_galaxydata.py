from galaxy_exporter.galaxy_exporter import GalaxyData


def test_galaxydata_defaults():
    gd = GalaxyData("test.test")
    assert gd.url() is None
    assert gd._setup_metrics() == dict()
