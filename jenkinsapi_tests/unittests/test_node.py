import mock
import unittest

from jenkinsapi.node import Node


class TestNode(unittest.TestCase):

    DATA = {"actions": [],
            "displayName": "bobnit",
            "executors": [{}],
            "icon": "computer.png",
            "idle": True,
            "jnlpAgent": False,
            "launchSupported": True,
            "loadStatistics": {},
            "manualLaunchAllowed": True,
            "monitorData": {"hudson.node_monitors.SwapSpaceMonitor": {"availablePhysicalMemory": 7681417216,
                                                                      "availableSwapSpace": 12195983360,
                                                                      "totalPhysicalMemory": 8374497280,
                                                                      "totalSwapSpace": 12195983360},
                            "hudson.node_monitors.ArchitectureMonitor": "Linux (amd64)",
                            "hudson.node_monitors.ResponseTimeMonitor": {"average": 64},
                            "hudson.node_monitors.TemporarySpaceMonitor": {"path": "/tmp", "size": 250172776448},
                            "hudson.node_monitors.DiskSpaceMonitor": {"path": "/home/sal/jenkins", "size": 170472026112},
                            "hudson.node_monitors.ClockMonitor": {"diff": 6736}},
            "numExecutors": 1,
            "offline": False,
            "offlineCause": None,
            "oneOffExecutors": [],
            "temporarilyOffline": False}

    @mock.patch.object(Node, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA

        # def __init__(self, baseurl, nodename, jenkins_obj):

        self.J = mock.MagicMock()  # Jenkins object
        self.n = Node('http://', 'bobnit', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        repr(self.n)

    def testName(self):
        with self.assertRaises(AttributeError):
            self.n.id()
        self.assertEquals(self.n.name, 'bobnit')

    @mock.patch.object(Node, '_poll')
    def test_online(self, _poll):
        _poll.return_value = self.DATA
        return self.assertEquals(self.n.is_online(), True)

if __name__ == '__main__':
    unittest.main()
