'''
System tests for `jenkinsapi.jenkins` module.
'''
import os
import re
import time
import gzip
import shutil
import tempfile
from jenkinsapi_tests.systests.job_configs import JOB_WITH_ARTIFACTS
from jenkinsapi_tests.test_utils.random_strings import random_string


def test_artefacts(jenkins):
    job_name = 'create_%s' % random_string()
    job = jenkins.create_job(job_name, JOB_WITH_ARTIFACTS)
    job.invoke(block=True)

    build = job.get_last_build()

    while build.is_running():
        time.sleep(1)

    artifacts = build.get_artifact_dict()
    assert isinstance(artifacts, dict) is True

    text_artifact = artifacts['out.txt']
    binary_artifact = artifacts['out.gz']

    tempDir = tempfile.mkdtemp()

    try:
        # Verify that we can handle text artifacts
        text_artifact.save_to_dir(tempDir, strict_validation=True)
        assert os.path.exists(os.path.join(tempDir, text_artifact.filename))
        readBackText = open(
            os.path.join(tempDir, text_artifact.filename),
            'rb').read().strip()
        readBackText = readBackText.decode('ascii')
        assert re.match(r'^PING \S+ \(127.0.0.1\)', readBackText) is not None
        assert readBackText.endswith('ms') is True

        # Verify that we can hande binary artifacts
        binary_artifact.save_to_dir(tempDir, strict_validation=True)
        assert os.path.exists(os.path.join(tempDir, binary_artifact.filename))
        readBackText = gzip.open(
            os.path.join(tempDir, binary_artifact.filename,),
            'rb').read().strip()
        readBackText = readBackText.decode('ascii')
        assert re.match(r'^PING \S+ \(127.0.0.1\)', readBackText) is not None
        assert readBackText.endswith('ms') is True
    finally:
        shutil.rmtree(tempDir)
