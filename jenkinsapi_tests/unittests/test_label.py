import pytest
from jenkinsapi.label import Label


DATA = {
    "actions": [],
    "busyExecutors": 0,
    "clouds": [],
    "description": None,
    "idleExecutors": 0,
    "loadStatistics": {},
    "name": "jenkins-slave",
    "nodes": [],
    "offline": True,
    "tiedJobs": [
        {
            "name": "test_job1",
            "url": "http://jtest:8080/job/test_job1/",
            "color": "blue"
        }, {
            "name": "test_job2",
            "url": "http://jtest:8080/job/test_job2/",
            "color": "blue"
        }, {
            "name": "test_job3",
            "url": "http://jtest:8080/job/test_job3/",
            "color": "blue"
        }, {
            "name": "test_job4",
            "url": "http://jtest:8080/job/test_job4/",
            "color": "blue"
        }
    ],
    "totalExecutors": 0,
    "propertiesList": []
}

DATA_JOB_NAMES = {
    "tiedJobs": [
        {"name": "test_job1"},
        {"name": "test_job2"},
        {"name": "test_job3"},
        {"name": "test_job4"}
    ]
}

DATA_JOBS = [
    {
        "url": "http://jtest:8080/job/test_job1/",
        "color": "blue",
        "name": "test_job1"
    }, {
        "url": "http://jtest:8080/job/test_job2/",
        "color": "blue",
        "name": "test_job2"
    }, {
        "url": "http://jtest:8080/job/test_job3/",
        "color": "blue",
        "name": "test_job3"
    }, {
        "url": "http://jtest:8080/job/test_job4/",
        "color": "blue",
        "name": "test_job4"
    }
]


@pytest.fixture(scope='function')
def label(monkeypatch, mocker):
    def fake_poll(cls, tree=None):  # pylint: disable=unused-argument
        return DATA

    monkeypatch.setattr(Label, '_poll', fake_poll)
    jenkins = mocker.MagicMock()

    return Label('http://foo:8080', 'jenkins-slave', jenkins)


def test_repr(label):
    # Can we produce a repr string for this object
    repr(label)


def test_name(label):
    with pytest.raises(AttributeError):
        label.id()
    assert label.labelname == 'jenkins-slave'


def test_get_tied_job_names(label):
    assert label.get_tied_job_names() == DATA_JOBS


def test_online(label):
    assert label.is_online() is False
