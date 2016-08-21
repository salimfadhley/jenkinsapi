'''
System tests for `jenkinsapi.jenkins` module.
'''
import os
import re
import time
import gzip
import shutil
import tempfile
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import JOB_WITH_ARTIFACTS
from jenkinsapi_tests.test_utils.random_strings import random_string


class TestPingerJob(BaseSystemTest):

    def test_artefacts(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_ARTIFACTS)
        job.invoke(block=True)

        b = job.get_last_build()

        while b.is_running():
            time.sleep(1)

        artifacts = b.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)

        text_artifact = artifacts['out.txt']
        binary_artifact = artifacts['out.gz']

        tempDir = tempfile.mkdtemp()

        try:
            # Verify that we can handle text artifacts
            text_artifact.save_to_dir(tempDir, strict_validation=True)
            readBackText = open(os.path.join(tempDir,
                                             text_artifact.filename),
                                'rb').read().strip()
            readBackText = readBackText.decode('ascii')
            self.assertTrue(re.match(r'^PING \S+ \(127.0.0.1\)', readBackText))
            self.assertTrue(readBackText.endswith('ms'))

            # Verify that we can hande binary artifacts
            binary_artifact.save_to_dir(tempDir, strict_validation=True)
            readBackText = gzip.open(os.path.join(tempDir,
                                                  binary_artifact.filename,),
                                     'rb').read().strip()
            readBackText = readBackText.decode('ascii')
            self.assertTrue(re.match(r'^PING \S+ \(127.0.0.1\)', readBackText))
            self.assertTrue(readBackText.endswith('ms'))
        finally:
            shutil.rmtree(tempDir)

if __name__ == '__main__':
    unittest.main()
