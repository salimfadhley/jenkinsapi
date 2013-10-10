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

if __name__ == '__main__':
    unittest.main()
