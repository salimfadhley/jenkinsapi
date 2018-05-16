import six
import pytest
from . import configs
from jenkinsapi.build import Build
from jenkinsapi.job import Job


@pytest.fixture(scope='function')
def jenkins(mocker):
    return mocker.MagicMock()


@pytest.fixture(scope='function')
def job(monkeypatch, jenkins):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return configs.JOB_DATA

    monkeypatch.setattr(Job, '_poll', fake_poll)

    fake_job = Job('http://', 'Fake_Job', jenkins)
    return fake_job


@pytest.fixture(scope='function')
def build(job, monkeypatch):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return configs.BUILD_SCM_DATA

    monkeypatch.setattr(Build, '_poll', fake_poll)

    return Build('http://', 97, job)


def test_git_scm(build):
    """
    Can we extract git build revision data from a build object?
    """
    assert isinstance(build.get_revision(), six.string_types)
    assert build.get_revision() == '7def9ed6e92580f37d00e4980c36c4d36e68f702'


def test_git_revision_branch(build):
    """
    Can we extract git build branch from a build object?
    """
    assert isinstance(build.get_revision_branch(), list)
    assert len(build.get_revision_branch()) == 1
    assert isinstance(build.get_revision_branch()[0], dict)
    assert build.get_revision_branch()[0]['SHA1'] == \
        '7def9ed6e92580f37d00e4980c36c4d36e68f702'
    assert build.get_revision_branch()[0]['name'] == 'origin/unstable'


def test_git_repo_url(build):
    """
     Can we Extract git repo url for a given build
    """
    assert isinstance(build.get_repo_url(), str)
    assert build.get_repo_url() == 'https://github.com/salimfadhley/jenkinsapi.git'
