import pytest
from jenkinsapi.node import Node


DATA = {
    "actions": [],
    "displayName": "bobnit",
    "executors": [{}],
    "icon": "computer.png",
    "idle": True,
    "jnlpAgent": False,
    "launchSupported": True,
    "loadStatistics": {},
    "manualLaunchAllowed": True,
    "monitorData": {
        "hudson.node_monitors.SwapSpaceMonitor": {
            "availablePhysicalMemory": 7681417216,
            "availableSwapSpace": 12195983360,
            "totalPhysicalMemory": 8374497280,
            "totalSwapSpace": 12195983360
        },
        "hudson.node_monitors.ArchitectureMonitor": "Linux (amd64)",
        "hudson.node_monitors.ResponseTimeMonitor": {"average": 64},
        "hudson.node_monitors.TemporarySpaceMonitor": {
            "path": "/tmp", "size": 250172776448
        },
        "hudson.node_monitors.DiskSpaceMonitor": {
            "path": "/home/sal/jenkins",
            "size": 170472026112
        },
        "hudson.node_monitors.ClockMonitor": {"diff": 6736}
    },
    "numExecutors": 1,
    "offline": False,
    "offlineCause": None,
    "oneOffExecutors": [],
    "temporarilyOffline": False
}


@pytest.fixture(scope='function')
def node(monkeypatch, mocker):
    def fake_poll(cls, tree=None):  # pylint: disable=unused-argument
        return DATA

    monkeypatch.setattr(Node, '_poll', fake_poll)
    jenkins = mocker.MagicMock()

    return Node(jenkins, 'http://foo:8080', 'bobnit', {})


def test_repr(node):
    # Can we produce a repr string for this object
    repr(node)


def test_name(node):
    with pytest.raises(AttributeError):
        node.id()
    assert node.name == 'bobnit'


def test_online(node):
    assert node.is_online() is True
