'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
import unittest
from StringIO import StringIO
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import JOB_WITH_FILE
from jenkinsapi_tests.systests.job_configs import JOB_WITH_PARAMETERS
from jenkinsapi.custom_exceptions import WillNotBuild


class TestParameterizedBuilds(BaseSystemTest):

    def test_invoke_job_with_file(self):
        file_data = random_string()
        param_file = StringIO(file_data)

        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_FILE)
        job.invoke(block=True, files={'file.txt': param_file})

        b = job.get_last_build()
        while b.is_running():
            time.sleep(0.25)

        artifacts = b.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        art_file = artifacts['file.txt']
        self.assertTrue(art_file.get_data().strip(), file_data)

    def test_invoke_job_parameterized(self):
        param_B = random_string()

        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)
        job.invoke(block=True, build_params={'B': param_B})

        b = job.get_last_build()
        while b.is_running():
            time.sleep(0.25)

        artifacts = b.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        artB = artifacts['b.txt']
        self.assertTrue(artB.get_data().strip(), param_B)

        self.assertIn(param_B, b.get_console())

    def test_parameterized_job_build_queuing(self):
        """Accept multiple builds of parameterized jobs with unique
           parameters."""
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)

        for i in range(3):
            param_B = random_string()
            params = {'B': param_B}
            job.invoke(build_params=params)

        self.assertTrue(job.has_queued_build(params))

        while(job.has_queued_build(params)):
            time.sleep(0.25)

        b = job.get_last_build()
        while b.is_running():
            time.sleep(0.25)

        artifacts = b.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        artB = artifacts['b.txt']
        self.assertTrue(artB.get_data().strip(), param_B)

        self.assertIn(param_B, b.get_console())

    def test_parameterized_job_build_rejection(self):
        """Reject build of paramterized job when existing build with same
           parameters is queued, raising WillNotBuild."""
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)

        for i in range(3):
            params = {'B': random_string()}
            job.invoke(build_params=params)

        with self.assertRaises(WillNotBuild) as na:
            job.invoke(build_params=params)
        expected_msg = 'A build with these parameters is already queued.'
        self.assertEqual(na.exception.message, expected_msg)


if __name__ == '__main__':
    unittest.main()
