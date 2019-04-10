"""
Queue module for jenkinsapi
"""
import logging
import time
from requests import HTTPError
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import UnknownQueueItem, NotBuiltYet

log = logging.getLogger(__name__)


class Queue(JenkinsBase):

    """
    Class that represents the Jenkins queue
    """

    def __init__(self, baseurl, jenkins_obj):
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
        return self.jenkins

    def iteritems(self):
        for item in self._data['items']:
            queue_id = item['id']
            item_baseurl = "%s/item/%i" % (self.baseurl, queue_id)
            yield item['id'], QueueItem(baseurl=item_baseurl,
                                        jenkins_obj=self.jenkins)

    def iterkeys(self):
        for item in self._data['items']:
            yield item['id']

    def itervalues(self):
        for item in self._data['items']:
            yield QueueItem(self.jenkins, **item)

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def __len__(self):
        return len(self._data['items'])

    def __getitem__(self, item_id):
        self_as_dict = dict(self.iteritems())
        if item_id in self_as_dict:
            return self_as_dict[item_id]
        else:
            raise UnknownQueueItem(item_id)

    def _get_queue_items_for_job(self, job_name):
        for item in self._data["items"]:
            if 'name' in item['task'] and item['task']['name'] == job_name:
                yield QueueItem(self.get_queue_item_url(item),
                                jenkins_obj=self.jenkins)

    def get_queue_items_for_job(self, job_name):
        return list(self._get_queue_items_for_job(job_name))

    def get_queue_item_url(self, item):
        return "%s/item/%i" % (self.baseurl, item["id"])

    def delete_item(self, queue_item):
        self.delete_item_by_id(queue_item.queue_id)

    def delete_item_by_id(self, item_id):
        deleteurl = '%s/cancelItem?id=%s' % (self.baseurl, item_id)
        self.get_jenkins_obj().requester.post_url(deleteurl)


class QueueItem(JenkinsBase):

    """An individual item in the queue
    """

    def __init__(self, baseurl, jenkins_obj):
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

    @property
    def queue_id(self):
        return self._data['id']

    @property
    def name(self):
        return self._data['task']['name']

    @property
    def why(self):
        return self._data.get('why')

    def get_jenkins_obj(self):
        return self.jenkins

    def get_job(self):
        """
        Return the job associated with this queue item
        """
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
        build_number = self.get_build_number()
        job = self.get_job()
        return job[build_number]

    def block_until_complete(self, delay=5):
        build = self.block_until_building(delay)
        return build.block_until_complete(delay=delay)

    def block_until_building(self, delay=5):
        while True:
            try:
                self.poll()
                return self.get_build()
            except (NotBuiltYet, HTTPError):
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
