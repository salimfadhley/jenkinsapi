import time
import json
import logging
import pytest

from six import StringIO
from six.moves.urllib.parse import urljoin
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
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


@pytest.fixture(scope='function')
def crumbed_jenkins(jenkins):
    jenkins.requester.post_and_confirm_status(
        urljoin(jenkins.baseurl, '/configureSecurity/configure'),
        data={
            'Submit': 'save',
            'json': json.dumps(ENABLE_CRUMBS_CONFIG)
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    crumbed = Jenkins(
        jenkins.baseurl,
        requester=CrumbRequester(baseurl=jenkins.baseurl)
    )
    yield crumbed

    crumbed.requester.post_and_confirm_status(
        jenkins.baseurl + '/configureSecurity/configure',
        data={
            'Submit': 'save',
            'json': json.dumps(DISABLE_CRUMBS_CONFIG)
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )


def test_invoke_job_with_file(crumbed_jenkins):
    file_data = random_string()
    param_file = StringIO(file_data)

    job_name = 'create1_%s' % random_string()
    job = crumbed_jenkins.create_job(job_name, JOB_WITH_FILE)

    assert job.has_params()
    assert len(job.get_params_list())

    job.invoke(block=True, files={'file.txt': param_file})

    build = job.get_last_build()
    while build.is_running():
        time.sleep(0.25)

    artifacts = build.get_artifact_dict()
    assert isinstance(artifacts, dict) is True
    art_file = artifacts['file.txt']
    assert art_file.get_data().decode('utf-8').strip() == file_data
