'''
System tests for `jenkinsapi.jenkins` module.
'''
import logging
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi.view import View
from jenkinsapi.views import Views
from jenkinsapi.job import Job
from jenkinsapi.api import get_view_from_url
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.view_configs import VIEW_WITH_FILTER_AND_REGEX
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
        self.assertEquals(view_name, str(v))

        # Can we use the API convenience methods
        v2 = get_view_from_url(v.baseurl)
        self.assertEquals(v, v2)

    def test_add_job_to_view(self):
        job_name = random_string()
        self._create_job(job_name)

        view_name = random_string()
        self.assertNotIn(view_name, self.jenkins.views)
        v = self.jenkins.views.create(view_name)
        self.assertIn(view_name, self.jenkins.views)
        self.assertIsInstance(v, View)

        self.assertNotIn(job_name, v)
        self.assertTrue(v.add_job(job_name))
        self.assertIn(job_name, v)
        self.assertIsInstance(v[job_name], Job)

        self.assertTrue(len(v) == 1)
        for j_name, j in v.iteritems():
            self.assertEquals(j_name, job_name)
            self.assertIsInstance(j, Job)

        for j in v.values():
            self.assertIsInstance(j, Job)

        jobs = v.items()
        self.assertIsInstance(jobs, list)
        self.assertIsInstance(jobs[0], tuple)

        self.assertFalse(v.add_job(job_name))
        self.assertFalse(v.add_job('unknown'))

        del self.jenkins.views[view_name]

    def test_create_and_delete_views(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views.create(view1_name)
        self.assertIsInstance(new_view, View)
        self.assertIn(view1_name, self.jenkins.views)
        del self.jenkins.views[view1_name]
        self.assertNotIn(view1_name, self.jenkins.views)

    def test_create_and_delete_views_by_url(self):
        self._create_job()
        view1_name = random_string()
        new_view = self.jenkins.views.create(view1_name)
        self.assertIsInstance(new_view, View)
        self.assertIn(view1_name, self.jenkins.views)
        view_url = new_view.baseurl
        view_by_url = self.jenkins.get_view_by_url(view_url)
        self.assertIsInstance(view_by_url, View)
        self.jenkins.delete_view_by_url(view_url)
        self.assertNotIn(view1_name, self.jenkins.views)

    def test_delete_view_which_does_not_exist(self):
        view1_name = random_string()
        self.assertNotIn(view1_name, self.jenkins.views)
        del self.jenkins.views[view1_name]

    def test_update_view_config(self):
        view_name = random_string()
        new_view = self.jenkins.views.create(view_name)
        self.assertIsInstance(new_view, View)
        self.assertIn(view_name, self.jenkins.views)
        config = self.jenkins.views[view_name].get_config().strip()
        new_view_config = VIEW_WITH_FILTER_AND_REGEX % view_name
        self.assertNotEquals(config, new_view_config)
        self.jenkins.views[view_name].update_config(new_view_config)
        config = self.jenkins.views[view_name].get_config().strip()
        self.assertEquals(config, new_view_config)

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
        self.assertTrue(job.name in sv2)

        # Can we use the API convenience methods
        v = get_view_from_url(sv2.baseurl)
        self.assertEquals(v, sv2)

    def test_add_to_view_after_copy(self):
        # This test is for issue #291
        job = self._create_job()
        new_job_name = random_string()
        view_name = random_string()
        new_view = self.jenkins.views.create(view_name)
        new_view = self.jenkins.views[view_name]
        new_job = self.jenkins.copy_job(job.name, new_job_name)
        self.assertTrue(new_view.add_job(new_job.name))
        self.assertIn(new_job.name, new_view)

    def test_get_job_config(self):
        # This test is for issue #301
        job = self._create_job()
        view_name = random_string()
        new_view = self.jenkins.views.create(view_name)

        self.assertTrue(new_view.add_job(job.name))

        self.assertIn('<?xml', self.jenkins.get_job(job.name).get_config())
        for job_name, job in self.jenkins.views[view_name].items():
            self.assertIn('<?xml', job.get_config())


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
