import pytz
import mock
import unittest
import datetime

try:
    import json
except ImportError:
    import simplejson as json

from jenkinsapi.jenkinsbase import JenkinsBase


class test_json(unittest.TestCase):

    DATA = {
        'actions': [
            { 'act1':  {'name': 'val' }},
            { 'act2':  {'name': 'val2' }}
            ],
        'post': [
            "post1",
            "post2",
        ]
        }

    def setUp(self):
        pass

    def test_json_to_str(self):
        jb = JenkinsBase("http://localhost", False)
        jdump = json.dumps(self.DATA)
        response_with_unicode = json.loads(jdump)
        response_with_str = json.loads(jdump, object_hook=jb._decode_dict)
        self.assertAlmostEqual(response_with_str,response_with_unicode, "Data structure is not the same")

        self.assertTrue(isinstance(response_with_str['actions'][0]['act1']['name'], str), "name is not string")
        self.assertTrue(isinstance(response_with_str['post'][0], str), "name is not string")


def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()
