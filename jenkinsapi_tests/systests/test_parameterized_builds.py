'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import JOB_WITH_FILE
from jenkinsapi_tests.systests.job_configs import JOB_WITH_FILE_AND_PARAMS
from jenkinsapi_tests.systests.job_configs import JOB_WITH_PARAMETERS


class TestParameterizedBuilds(BaseSystemTest):

    def test_invoke_job_with_file(self):
        file_data = random_string()
        param_file = StringIO(file_data)

        job_name = 'create1_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_FILE)

        self.assertTrue(job.has_params())
        self.assertTrue(len(job.get_params_list()) != 0)

        job.invoke(block=True, files={'file.txt': param_file})

        build = job.get_last_build()
        while build.is_running():
            time.sleep(0.25)

        artifacts = build.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        art_file = artifacts['file.txt']
        self.assertTrue(art_file.get_data().strip(), file_data)

    def test_invoke_job_parameterized(self):
        param_B = random_string()

        job_name = 'create2_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)
        job.invoke(block=True, build_params={'B': param_B})
        build = job.get_last_build()

        artifacts = build.get_artifact_dict()
        artB = artifacts['b.txt']
        self.assertEqual(
            artB.get_data().strip().decode('UTF-8', 'replace'),
            param_B,
        )

        self.assertIn(param_B, build.get_console())

    def test_parameterized_job_build_queuing(self):
        """Accept multiple builds of parameterized jobs with unique
           parameters."""
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)

        for i in range(3):
            param_B = random_string()
            params = {'B': param_B}
            job.invoke(build_params=params)
            time.sleep(0.25)

        self.assertTrue(job.has_queued_build(params))

        while job.has_queued_build(params):
            time.sleep(0.25)

        build = job.get_last_build()
        while build.is_running():
            time.sleep(0.25)

        artifacts = build.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        artB = artifacts['b.txt']
        self.assertTrue(artB.get_data().strip(), param_B)

        self.assertIn(param_B, build.get_console())

    def test_parameterized_multiple_builds_get_the_same_queue_item(self):
        """Multiple attempts to run the same parameterized
        build will get the same queue item."""
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_PARAMETERS)

        for i in range(3):
            params = {'B': random_string()}
            qq0 = job.invoke(build_params=params)

        qq1 = job.invoke(build_params=params)
        self.assertEqual(qq0, qq1)

    def test_invoke_job_with_file_and_params(self):
        file_data = random_string()
        param_data = random_string()
        param_file = StringIO(file_data)

        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_FILE_AND_PARAMS)

        self.assertTrue(job.has_params())
        self.assertTrue(len(job.get_params_list()) != 0)

        qi = job.invoke(
            block=True,
            files={'file.txt': param_file},
            build_params={'B': param_data}
        )

        build = qi.get_build()
        artifacts = build.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)
        art_file = artifacts['file.txt']
        self.assertTrue(art_file.get_data().strip(), file_data)
        art_param = artifacts['file1.txt']
        self.assertTrue(art_param.get_data().strip(), param_data)


if __name__ == '__main__':
    unittest.main()
