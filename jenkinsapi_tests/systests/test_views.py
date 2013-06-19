'''
System tests for `jenkinsapi.jenkins` module.
'''
import logging
import unittest

from jenkinsapi.view import View
from jenkinsapi.api import get_view_from_url
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string

log = logging.getLogger(__name__)


class TestViews(BaseSystemTest):
    def test_make_views(self):
        self._create_job()
        view_name = random_string()
        self.assertNotIn(view_name, self.jenkins.views())
        v = self.jenkins.views().create(view_name)
        self.assertIn(view_name, self.jenkins.views())
        self.assertIsInstance(v, View)

        # Can we use the API comnvenience methods
        v2 = get_view_from_url(v.baseurl)
        self.assertEquals(v, v2)

    def test_create_and_delete_views(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views().create(view1_name)
        self.assertIsInstance(new_view, View)
        self.assertIn(view1_name, self.jenkins.views())
        del self.jenkins.views()[view1_name]
        self.assertNotIn(view1_name, self.jenkins.views())

    def test_delete_view_which_does_not_exist(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views().create(view1_name)
        self.assertIn(view1_name, self.jenkins.views())
        del self.jenkins.views()[view1_name]

        with self.assertRaises(KeyError):
            del self.jenkins.views()[view1_name]



if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
