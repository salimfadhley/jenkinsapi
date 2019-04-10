import pytest
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.queue import QueueItem


@pytest.fixture(scope='function')
def jenkins(monkeypatch):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)
    new_jenkins = Jenkins('http://halob:8080/')

    return new_jenkins


@pytest.fixture(scope='function')
def queueitem(jenkins, monkeypatch):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(QueueItem, '_poll', fake_poll)

    new_queue = QueueItem('http://halob:8080/queue/item/1', jenkins)

    return new_queue


def test_get_full_name_from_url_and_baseurl(queueitem):
    job_name = 'fake_job_name'
    base_url = queueitem.jenkins.baseurl
    job_url_name = '{0}/job/{1}'.format(base_url, job_name)
    job_queueitem_name = queueitem.get_full_name_from_url_and_baseurl(job_url_name,
                                                                      base_url)
    assert job_queueitem_name == job_name


def test_get_full_name_from_url_and_baseurl_withfolder(queueitem):
    job_name = 'fake_job_name'
    folder_name = 'fake_folder_name'

    job_full_name = '{0}/{1}'.format(folder_name, job_name)
    base_url = queueitem.jenkins.baseurl
    job_url_name = '{0}/job/{1}/job/{2}'.format(base_url, folder_name, job_name)

    job_queueitem_name = queueitem.get_full_name_from_url_and_baseurl(job_url_name,
                                                                      base_url)
    assert job_queueitem_name == job_full_name


def test_get_job_name(queueitem):
    job_name = 'fake_job_name'
    base_url = queueitem.jenkins.baseurl

    job_url_name = '{0}/job/{1}'.format(base_url, job_name)

    queueitem._data = {'task': {'name': job_name, 'url': job_url_name}}

    assert queueitem.get_job_name() == job_name


def test_get_job_name_withfolder(queueitem):
    job_name = 'fake_job_name'
    folder_name = 'fake_folder_name'
    base_url = queueitem.jenkins.baseurl

    job_url_name = '{0}/job/{1}/job/{2}'.format(base_url, folder_name, job_name)
    job_full_name = '{0}/{1}'.format(folder_name, job_name)

    queueitem._data = {'task': {'name': job_name, 'url': job_url_name}}

    assert queueitem.get_job_name() == job_full_name
