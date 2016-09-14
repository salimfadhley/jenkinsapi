# To run unittests on python 2.6 please use unittest2 library
import time
import json
import logging
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
import jenkinsapi_tests.systests
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import JOB_WITH_FILE

log = logging.getLogger(__name__)

DEFAULT_JENKINS_PORT = 8080
ENABLE_CRUMBS_CONFIG = {
    '': '0',
    'markupFormatter': {
      'stapler-class': 'hudson.markup.EscapedMarkupFormatter',
      '$class': 'hudson.markup.EscapedMarkupFormatter'
    },
    'hudson-security-csrf-GlobalCrumbIssuerConfiguration': {
      'csrf': {
        'issuer': {
          'value': '0',
          'stapler-class': 'hudson.security.csrf.DefaultCrumbIssuer',
          '$class': 'hudson.security.csrf.DefaultCrumbIssuer',
          'excludeClientIPFromCrumb': False
        }
      }
    },
    'jenkins-model-DownloadSettings': {
      'useBrowser': False
    },
    'core:apply': '',
}
DISABLE_CRUMBS_CONFIG = {
    '': '0',
    'markupFormatter': {
      'stapler-class': 'hudson.markup.EscapedMarkupFormatter',
      '$class': 'hudson.markup.EscapedMarkupFormatter'
    },
    'hudson-security-csrf-GlobalCrumbIssuerConfiguration': {},
    'jenkins-model-DownloadSettings': {
      'useBrowser': False
    },
    'core:apply': ''
  }


class TestCrumbsRequester(unittest.TestCase):
    def setUp(self):
        try:
            port = jenkinsapi_tests.systests.state['launcher'].http_port
        except KeyError:
            log.warning(
                "Jenkins was not launched from the test-framework, "
                "assuming port %i" %
                DEFAULT_JENKINS_PORT)
            port = DEFAULT_JENKINS_PORT
        self.jenkins = Jenkins('http://localhost:%d' % port)

        self.jenkins.requester.post_and_confirm_status(
            self.jenkins.baseurl + '/configureSecurity/configure',
            data={
                'Submit': 'save',
                'json': json.dumps(ENABLE_CRUMBS_CONFIG)
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        self.jenkins = Jenkins(
            self.jenkins.baseurl,
            requester=CrumbRequester(baseurl=self.jenkins.baseurl))

    def tearDown(self):
        self.jenkins.requester.post_and_confirm_status(
            self.jenkins.baseurl + '/configureSecurity/configure',
            data={
                'Submit': 'save',
                'json': json.dumps(DISABLE_CRUMBS_CONFIG)
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

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
