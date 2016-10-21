import jenkinsapi


def test_jenkinsapi_version():
    """Verify that we can get the jenkinsapi version number from the
    package's __version__ property.
    """
    version = jenkinsapi.__version__
    parts = [int(x) for x in version.split('.')]
    for part in parts:
        assert part >= 0, "Implausible version number: %r" % version
