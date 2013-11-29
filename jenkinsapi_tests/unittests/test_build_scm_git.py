import mock
import unittest
from jenkinsapi.build import Build


class test_build(unittest.TestCase):

    DATA = {
        'actions': [
            {
                'causes': [{'shortDescription': 'Started by an SCM change'}]
            },
            {},
            {
                'buildsByBranchName': {
                    'origin/HEAD': {
                        'buildNumber': 2,
                        'buildResult': None,
                        'revision': {
                            'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2',
                            'branch': [
                                {'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2', 'name': 'origin/HEAD'},
                                {'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2', 'name': 'origin/master'}
                            ]
                        }
                    },
                    'origin/master': {
                        'buildNumber': 2,
                        'buildResult': None,
                        'revision': {
                            'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2',
                            'branch': [
                                {'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2', 'name': 'origin/HEAD'},
                                {'SHA1': 'd2a5d435fa2df3bff572bd06e43c86544749c5d2', 'name': 'origin/master'}
                            ]
                        }
                    },
                    'origin/python_3_compatibility': {
                        'buildNumber': 1,
                        'buildResult': None,
                        'revision': {
                            'SHA1': 'c9d1c96bc926ff63a5209c51b3ed537e62ea50e6',
                            'branch': [
                                {'SHA1': 'c9d1c96bc926ff63a5209c51b3ed537e62ea50e6', 'name': 'origin/python_3_compatibility'}
                            ]
                        }
                    },
                    'origin/unstable': {
                        'buildNumber': 3,
                        'buildResult': None,
                        'revision': {
                            'SHA1': '7def9ed6e92580f37d00e4980c36c4d36e68f702',
                            'branch': [
                                {'SHA1': '7def9ed6e92580f37d00e4980c36c4d36e68f702', 'name': 'origin/unstable'}
                            ]
                        }
                    }
                },
                'lastBuiltRevision': {
                    'SHA1': '7def9ed6e92580f37d00e4980c36c4d36e68f702',
                    'branch': [
                        {'SHA1': '7def9ed6e92580f37d00e4980c36c4d36e68f702', 'name': 'origin/unstable'}
                    ]
                },
                'remoteUrls': ['https://github.com/salimfadhley/jenkinsapi.git'],
                'scmName': ''
            },
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'builtOn': '',
        'changeSet': {'items': [], 'kind': 'git'},
        'culprits': [],
        'description': None,
        'duration': 1051,
        'estimatedDuration': 2260,
        'executor': None,
        'fullDisplayName': 'git_yssrtigfds #3',
        'id': '2013-06-30_01-54-35',
        'keepLog': False,
        'number': 3,
        'result': 'SUCCESS',
        'timestamp': 1372553675652,
        'url': 'http://localhost:8080/job/git_yssrtigfds/3/'
    }

    @mock.patch.object(Build, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA
        self.j = mock.MagicMock()  # Job
        self.j.name = 'FooJob'

        self.b = Build('http://', 97, self.j)

    def test_git_scm(self):
        """
        Can we extract git build revision data from a build object?
        """
        self.assertIsInstance(self.b.get_revision(), basestring)
        self.assertEquals(self.b.get_revision(),
                          '7def9ed6e92580f37d00e4980c36c4d36e68f702')

    def test_git_revision_branch(self):
        """
        Can we extract git build branch from a build object?
        """
        self.assertIsInstance(self.b.get_revision_branch(), list)
        self.assertEquals(len(self.b.get_revision_branch()), 1)
        self.assertIsInstance(self.b.get_revision_branch()[0], dict)
        self.assertEquals(self.b.get_revision_branch()[0]['SHA1'],
                          '7def9ed6e92580f37d00e4980c36c4d36e68f702')
        self.assertEquals(self.b.get_revision_branch()[0]['name'],
                          'origin/unstable')

if __name__ == '__main__':
    unittest.main()
