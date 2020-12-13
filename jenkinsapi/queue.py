"""
Queue module for jenkinsapi
"""
import logging
import time
from requests import HTTPError
from typing import Any, Dict, Iterator, List, Tuple, TYPE_CHECKING
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import UnknownQueueItem, NotBuiltYet

if TYPE_CHECKING:
    from jenkinsapi.build import Build
    from jenkinsapi.jenkins import Jenkins
    from jenkinsapi.job import Job


log = logging.getLogger(__name__)


class Queue(JenkinsBase):

    """
    Class that represents the Jenkins queue
    """

    def __init__(self, baseurl, jenkins_obj):
        # type: (str, Jenkins) -> None
        """
        Init the Jenkins queue object
        :param baseurl: basic url for the queue
        :param jenkins_obj: ref to the jenkins obj
        """
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

    def __str__(self):
        return self.baseurl

    def get_jenkins_obj(self):
        # type: () -> Jenkins
        return self.jenkins

    def iteritems(self):
        # type: () -> Iterator[Tuple[str, QueueItem]]
        assert self._data is not None
        for item in self._data['items']:
            queue_id = item['id']
            item_baseurl = "%s/item/%i" % (self.baseurl, queue_id)
            yield item['id'], QueueItem(baseurl=item_baseurl,
                                        jenkins_obj=self.jenkins)

    def iterkeys(self):
        # type: () -> Iterator[str]
        assert self._data is not None
        for item in self._data['items']:
            yield item['id']

    def itervalues(self):
        # type: () -> Iterator[QueueItem]
        assert self._data is not None
        for item in self._data['items']:
            # FIXME: QueueItem() does not get the right arguments here.
            # broken by commit a4c3fab827673da3c70e834ffd4d362f24190de1
            # remove the type ignore once fixed.
            yield QueueItem(self.jenkins, **item)   # type: ignore

    def keys(self):
        # type: () -> List[str]
        return list(self.iterkeys())

    def values(self):
        # type: () -> List[QueueItem]
        return list(self.itervalues())

    def __len__(self):
        return len(self._data['items'])

    def __getitem__(self, item_id):
        # type: (str) -> QueueItem
        self_as_dict = dict(self.iteritems())
        if item_id in self_as_dict:
            return self_as_dict[item_id]
        else:
            raise UnknownQueueItem(item_id)

    def _get_queue_items_for_job(self, job_name):
        # type: (str) -> Iterator[QueueItem]
        assert self._data is not None
        for item in self._data["items"]:
            if 'name' in item['task'] and item['task']['name'] == job_name:
                yield QueueItem(self.get_queue_item_url(item),
                                jenkins_obj=self.jenkins)

    def get_queue_items_for_job(self, job_name):
        # type: (str) -> List[QueueItem]
        return list(self._get_queue_items_for_job(job_name))

    def get_queue_item_url(self, item):
        # type: (Dict[str, Any]) -> str
        return "%s/item/%i" % (self.baseurl, item["id"])

    def delete_item(self, queue_item):
        # type: (QueueItem) -> None
        self.delete_item_by_id(queue_item.queue_id)

    def delete_item_by_id(self, item_id):
        # type: (str) -> None
        deleteurl = '%s/cancelItem?id=%s' % (self.baseurl, item_id)
        self.get_jenkins_obj().requester.post_url(deleteurl)


class QueueItem(JenkinsBase):

    """An individual item in the queue
    """

    def __init__(self, baseurl, jenkins_obj):
        # type: (str, Jenkins) -> None
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

    @property
    def queue_id(self):
        # type: () -> str
        assert self._data is not None
        return self._data['id']

    @property
    def name(self):
        # type: () -> str
        assert self._data is not None
        return self._data['task']['name']

    @property
    def why(self):
        assert self._data is not None
        return self._data.get('why')

    def get_jenkins_obj(self):
        # type: () -> Jenkins
        return self.jenkins

    def get_job(self):
        # type: () -> Job
        """
        Return the job associated with this queue item
        """
        assert self._data is not None
        return self.jenkins.get_job_by_url(
            self._data['task']['url'],
            self._data['task']['name'],
        )

    def get_parameters(self):
        """returns parameters of queue item"""
        actions = self._data.get('actions', [])
        for action in actions:
            if isinstance(action, dict) and 'parameters' in action:
                parameters = action['parameters']
                return dict([(x['name'], x.get('value', None))
                             for x in parameters])
        return []

    def __repr__(self):
        return "<%s.%s %s>" % (self.__class__.__module__,
                               self.__class__.__name__, str(self))

    def __str__(self):
        return "%s Queue #%i" % (self.name, self.queue_id)

    def get_build(self):
        # type: () -> Build
        build_number = self.get_build_number()
        job = self.get_job()
        return job[build_number]

    def block_until_complete(self, delay=5):
        build = self.block_until_building(delay)
        return build.block_until_complete(delay=delay)

    def block_until_building(self, delay=5):
        # type: (int) -> Build
        while True:
            try:
                self.poll()
                return self.get_build()
            except NotBuiltYet:
                time.sleep(delay)
                continue
            except HTTPError as http_error:
                log.debug(str(http_error))
                time.sleep(delay)
                continue

    def is_running(self):
        """Return True if this queued item is running.
        """
        try:
            return self.get_build().is_running()
        except NotBuiltYet:
            return False

    def is_queued(self):
        """Return True if this queued item is queued.
        """
        try:
            self.get_build()
            return False
        except NotBuiltYet:
            return True

    def get_build_number(self):
        try:
            return self._data['executable']['number']
        except (KeyError, TypeError):
            raise NotBuiltYet()

    def get_job_name(self):
        try:
            return self._data['task']['name']
        except KeyError:
            raise NotBuiltYet()
