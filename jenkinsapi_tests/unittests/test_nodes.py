import pytest
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.nodes import Nodes
from jenkinsapi.node import Node


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


@pytest.fixture(scope='function')
def nodes(monkeypatch):
    def fake_jenkins_poll(cls, tree=None):  # pylint: disable=unused-argument
        return DATA0

    monkeypatch.setattr(Jenkins, '_poll', fake_jenkins_poll)

    def fake_nodes_poll(cls, tree=None):  # pylint: disable=unused-argument
        return DATA1

    monkeypatch.setattr(Nodes, '_poll', fake_nodes_poll)
    jenkins = Jenkins('http://foo:8080')
    return jenkins.get_nodes()


def fake_node_poll(self, tree=None):  # pylint: disable=unused-argument
    """
    Fakes a poll of data by returning the correct section of the DATA1 test block.
    """
    for node_poll in DATA1['computer']:
        if node_poll['displayName'] == self.name:
            return node_poll
    return DATA2


def test_repr(nodes):
    # Can we produce a repr string for this object
    repr(nodes)


def test_baseurl(nodes):
    assert nodes.baseurl == 'http://foo:8080/computer'


def test_get_master_node(nodes, monkeypatch):
    monkeypatch.setattr(Node, '_poll', fake_node_poll)

    node = nodes['master']
    assert isinstance(node, Node)


def test_get_nonmaster_node(nodes, monkeypatch):
    monkeypatch.setattr(Node, '_poll', fake_node_poll)

    node = nodes['halob']
    assert isinstance(node, Node)


def test_iterkeys(nodes):
    expected_names = set(['master', 'bobnit', 'halob'])
    actual_names = set([n for n in nodes.iterkeys()])
    assert actual_names == expected_names


def test_keys(nodes):
    expected_names = set(['master', 'bobnit', 'halob'])
    actual_names = set(nodes.keys())
    assert actual_names == expected_names


def items_test_case(nodes_method, monkeypatch):
    monkeypatch.setattr(Node, '_poll', fake_node_poll)

    expected_names = set(['master', 'bobnit', 'halob'])

    actual_names = set()
    for name, node in nodes_method():
        assert name == node.name
        assert isinstance(node, Node)

        actual_names.add(name)

    assert actual_names == expected_names


def test_iteritems(nodes, monkeypatch):
    items_test_case(nodes.iteritems, monkeypatch)


def test_items(nodes, monkeypatch):
    items_test_case(nodes.items, monkeypatch)


def values_test_case(nodes_method, monkeypatch):
    monkeypatch.setattr(Node, '_poll', fake_node_poll)

    expected_names = set(['master', 'bobnit', 'halob'])

    actual_names = set()
    for node in nodes_method():
        assert isinstance(node, Node)
        actual_names.add(node.name)

    assert actual_names == expected_names


def test_itervalues(nodes, monkeypatch):
    values_test_case(nodes.itervalues, monkeypatch)


def test_values(nodes, monkeypatch):
    values_test_case(nodes.values, monkeypatch)
