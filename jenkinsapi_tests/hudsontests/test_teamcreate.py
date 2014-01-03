'''
Tests that jobs can be created in different teams
'''
import unittest
import time
from jenkinsapi.build import Build
from jenkinsapi.invocation import Invocation
from jenkinsapi_tests.hudsontests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.hudsontests.job_configs import LONG_RUNNING_JOB
from jenkinsapi_tests.hudsontests.job_configs import SHORTISH_JOB, EMPTY_JOB


class TestTeamCreate(BaseSystemTest):

    def test_create_public_job(self):
        """
        Can we create a regular public job?
        """
        job_name = 'create_%s' % random_string()
        job = self.hudson.create_job(job_name, SHORTISH_JOB)

        self.assertEqual(job_name, job.name)
        self.assertJobIsPresent(job_name)

        ii = job.invoke(invoke_pre_check_delay=7)
        self.assertIsInstance(ii, Invocation)
        # Let hudson catchup
        time.sleep(3)
        self.assertTrue(ii.is_queued_or_running())
        self.assertEquals(ii.get_build_number(), 1)

    def test_create_team_job(self):
        """
        Can we create a job in a team?
        """
        job_name = 'create_%s' % random_string()
        full_job_name ="one." +job_name
        job = self.hudson.create_job(job_name, SHORTISH_JOB,"one")

        self.assertEqual(full_job_name, job.name)
        self.assertJobIsPresent(full_job_name)

        ii = job.invoke(invoke_pre_check_delay=7)
        self.assertIsInstance(ii, Invocation)
        # Let hudson catchup
        time.sleep(3)
        self.assertTrue(ii.is_queued_or_running())
        self.assertEquals(ii.get_build_number(), 1)

    def test_create_same_job_in_different_teams(self):
        """
        Can we create the same job in different teams?
        """

        job_name = 'create_%s' % random_string()
        team_one_job = self.hudson.create_job(job_name, SHORTISH_JOB,"one")
        team_two_job = self.hudson.create_job(job_name, SHORTISH_JOB,"two")
        public_job = self.hudson.create_job(job_name, SHORTISH_JOB)

        self.assertEqual("one." + job_name, team_one_job.name)
        self.assertEqual("two." + job_name, team_two_job.name)
        self.assertEqual(job_name, public_job.name)

        self.assertJobIsPresent(job_name)
        self.assertJobIsPresent("one." + job_name)
        self.assertJobIsPresent("two." + job_name)




if __name__ == '__main__':
    unittest.main()
