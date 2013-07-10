'''
System tests for `jenkinsapi.jenkins` module.
'''
import logging
import unittest

from jenkinsapi.view import View
from jenkinsapi.views import Views
from jenkinsapi.api import get_view_from_url
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string

log = logging.getLogger(__name__)


class TestViews(BaseSystemTest):
    def test_make_views(self):
        self._create_job()
        view_name = random_string()
        self.assertNotIn(view_name, self.jenkins.views)
        v = self.jenkins.views.create(view_name)
        self.assertIn(view_name, self.jenkins.views)
        self.assertIsInstance(v, View)

        # Can we use the API convenience methods
        v2 = get_view_from_url(v.baseurl)
        self.assertEquals(v, v2)

    def test_create_and_delete_views(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views.create(view1_name)
        self.assertIsInstance(new_view, View)
        self.assertIn(view1_name, self.jenkins.views)
        del self.jenkins.views[view1_name]
        self.assertNotIn(view1_name, self.jenkins.views)

    def test_delete_view_which_does_not_exist(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views.create(view1_name)
        self.assertIn(view1_name, self.jenkins.views)
        del self.jenkins.views[view1_name]
        self.assertNotIn(view1_name, self.jenkins.views)

    def test_make_nested_views(self):
        job = self._create_job()
        top_view_name = random_string()
        sub1_view_name = random_string()
        sub2_view_name = random_string()

        self.assertNotIn(top_view_name, self.jenkins.views)
        tv = self.jenkins.views.create(top_view_name, Views.NESTED_VIEW)
        self.assertIn(top_view_name, self.jenkins.views)
        self.assertIsInstance(tv, View)

        # Empty sub view
        sv1 = tv.views.create(sub1_view_name) 
        self.assertIn(sub1_view_name, tv.views)
        self.assertIsInstance(sv1, View)

        # Sub view with job in it
        tv.views[sub2_view_name] = job.name
        self.assertIn(sub2_view_name, tv.views)
        sv2 = tv.views[sub2_view_name]
        self.assertIsInstance(sv2, View)
        print 'job.name, type(job.name)=', job.name, type(job.name)
        self.assertTrue(job.name in sv2)

        # Can we use the API convenience methods
        v = get_view_from_url(sv2.baseurl)
        self.assertEquals(v, sv2)

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
