import mock
import unittest

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.nodes import Nodes
from jenkinsapi.node import Node


class TestNode(unittest.TestCase):

    DATA0 = {
        'assignedLabels': [{}],
        'description': None,
        'jobs': [],
        'mode': 'NORMAL',
        'nodeDescription': 'the master Jenkins node',
        'nodeName': '',
        'numExecutors': 2,
        'overallLoad': {},
        'primaryView': {'name': 'All', 'url': 'http://halob:8080/'},
        'quietingDown': False,
        'slaveAgentPort': 0,
        'unlabeledLoad': {},
        'useCrumbs': False,
        'useSecurity': False,
        'views': [
            {'name': 'All', 'url': 'http://halob:8080/'},
            {'name': 'FodFanFo', 'url': 'http://halob:8080/view/FodFanFo/'}
        ]
    }

    DATA1 = {
        'busyExecutors': 0,
        'computer': [
            {
                'actions': [],
                'displayName': 'master',
                'executors': [{}, {}],
                'icon': 'computer.png',
                'idle': True,
                'jnlpAgent': False,
                'launchSupported': True,
                'loadStatistics': {},
                'manualLaunchAllowed': True,
                'monitorData': {
                    'hudson.node_monitors.ArchitectureMonitor': 'Linux (amd64)',
                    'hudson.node_monitors.ClockMonitor': {'diff': 0},
                    'hudson.node_monitors.DiskSpaceMonitor': {
                        'path': '/var/lib/jenkins',
                        'size': 671924924416
                    },
                    'hudson.node_monitors.ResponseTimeMonitor': {'average': 0},
                    'hudson.node_monitors.SwapSpaceMonitor': {
                        'availablePhysicalMemory': 3174686720,
                        'availableSwapSpace': 17163087872,
                        'totalPhysicalMemory': 16810180608,
                        'totalSwapSpace': 17163087872
                    },
                    'hudson.node_monitors.TemporarySpaceMonitor': {
                        'path': '/tmp',
                        'size': 671924924416
                    }
                },
                'numExecutors': 2,
                'offline': False,
                'offlineCause': None,
                'oneOffExecutors': [],
                'temporarilyOffline': False
            },
            {
                'actions': [],
                'displayName': 'bobnit',
                'executors': [{}],
                'icon': 'computer-x.png',
                'idle': True,
                'jnlpAgent': False,
                'launchSupported': True,
                'loadStatistics': {},
                'manualLaunchAllowed': True,
                'monitorData': {
                    'hudson.node_monitors.ArchitectureMonitor': 'Linux (amd64)',
                    'hudson.node_monitors.ClockMonitor': {'diff': 4261},
                    'hudson.node_monitors.DiskSpaceMonitor': {
                        'path': '/home/sal/jenkins',
                        'size': 169784860672
                    },
                    'hudson.node_monitors.ResponseTimeMonitor': {'average': 29},
                    'hudson.node_monitors.SwapSpaceMonitor': {
                        'availablePhysicalMemory': 4570710016,
                        'availableSwapSpace': 12195983360,
                        'totalPhysicalMemory': 8374497280,
                        'totalSwapSpace': 12195983360
                    },
                    'hudson.node_monitors.TemporarySpaceMonitor': {
                        'path': '/tmp',
                        'size': 249737277440
                    }
                },
                'numExecutors': 1,
                'offline': True,
                'offlineCause': {},
                'oneOffExecutors': [],
                'temporarilyOffline': False
            },
            {
                'actions': [],
                'displayName': 'halob',
                'executors': [{}],
                'icon': 'computer-x.png',
                'idle': True,
                'jnlpAgent': True,
                'launchSupported': False,
                'loadStatistics': {},
                'manualLaunchAllowed': True,
                'monitorData': {
                    'hudson.node_monitors.ArchitectureMonitor': None,
                    'hudson.node_monitors.ClockMonitor': None,
                    'hudson.node_monitors.DiskSpaceMonitor': None,
                    'hudson.node_monitors.ResponseTimeMonitor': None,
                    'hudson.node_monitors.SwapSpaceMonitor': None,
                    'hudson.node_monitors.TemporarySpaceMonitor': None
                },
                'numExecutors': 1,
                'offline': True,
                'offlineCause': None,
                'oneOffExecutors': [],
                'temporarilyOffline': False
            }
        ],
        'displayName': 'nodes',
        'totalExecutors': 2
    }

    DATA2 = {
        'actions': [],
        'displayName': 'master',
        'executors': [{}, {}],
        'icon': 'computer.png',
        'idle': True,
        'jnlpAgent': False,
        'launchSupported': True,
        'loadStatistics': {},
        'manualLaunchAllowed': True,
        'monitorData': {
            'hudson.node_monitors.ArchitectureMonitor': 'Linux (amd64)',
            'hudson.node_monitors.ClockMonitor': {'diff': 0},
            'hudson.node_monitors.DiskSpaceMonitor': {
                'path': '/var/lib/jenkins',
                'size': 671942561792
            },
            'hudson.node_monitors.ResponseTimeMonitor': {'average': 0},
            'hudson.node_monitors.SwapSpaceMonitor': {
                'availablePhysicalMemory': 2989916160,
                'availableSwapSpace': 17163087872,
                'totalPhysicalMemory': 16810180608,
                'totalSwapSpace': 17163087872
            },
            'hudson.node_monitors.TemporarySpaceMonitor': {
                'path': '/tmp',
                'size': 671942561792
            }
        },
        'numExecutors': 2,
        'offline': False,
        'offlineCause': None,
        'oneOffExecutors': [],
        'temporarilyOffline': False
    }

    DATA3 = {
        'actions': [],
        'displayName': 'halob',
        'executors': [{}],
        'icon': 'computer-x.png',
        'idle': True,
        'jnlpAgent': True,
        'launchSupported': False,
        'loadStatistics': {},
        'manualLaunchAllowed': True,
        'monitorData': {
            'hudson.node_monitors.ArchitectureMonitor': None,
            'hudson.node_monitors.ClockMonitor': None,
            'hudson.node_monitors.DiskSpaceMonitor': None,
            'hudson.node_monitors.ResponseTimeMonitor': None,
            'hudson.node_monitors.SwapSpaceMonitor': None,
            'hudson.node_monitors.TemporarySpaceMonitor': None},
        'numExecutors': 1,
        'offline': True,
        'offlineCause': None,
        'oneOffExecutors': [],
        'temporarilyOffline': False
    }

    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Nodes, '_poll')
    def setUp(self, _poll_nodes, _poll_jenkins):
        _poll_jenkins.return_value = self.DATA0
        _poll_nodes.return_value = self.DATA1

        # def __init__(self, baseurl, nodename, jenkins_obj):

        self.J = Jenkins('http://localhost:8080')
        self.ns = self.J.get_nodes()
        # self.ns = Nodes('http://localhost:8080/computer', 'bobnit', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        repr(self.ns)

    def testCheckURL(self):
        self.assertEquals(self.ns.baseurl, 'http://localhost:8080/computer')

    @mock.patch.object(Node, '_poll')
    def testGetMasterNode(self, _poll_node):
        _poll_node.return_value = self.DATA2
        mn = self.ns['master']
        self.assertIsInstance(mn, Node)

    @mock.patch.object(Node, '_poll')
    def testGetNonMasterNode(self, _poll_node):
        _poll_node.return_value = self.DATA3
        mn = self.ns['halob']
        self.assertIsInstance(mn, Node)

if __name__ == '__main__':
    unittest.main()
