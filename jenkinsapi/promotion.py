"""
A jenkins promotion represents a single execution of a Jenkins promotion.

Promotions can be thought of as the third level of the jenkins heirarchy
beneath Jobs and Builds. Promotions can have state, such as whether they are running or
not. They can also have outcomes, such as wether they passed or failed.

Promotions depend on the presence of the promoted-builds plugin in Jenkins
"""
import json
import logging

from jenkinsapi.jenkinsbase import JenkinsBase
from time import sleep

log = logging.getLogger(__name__)

class PromotionBuild(JenkinsBase):
    def __init__(self, build, url):
        self.build = build
        JenkinsBase.__init__(self,url)

    def _poll(self, tree=None):
        # Promotion plugin only provides a json api.
        url = self.json_api_url(self.baseurl)
        raw_data = self.build.get_raw_data(url)
        return json.loads(raw_data)
        
    def get_status(self):
        return self._data['result']

    def get_number(self):
        return self._data['number']

    def is_running(self):
        """
        Return a bool if running.
        """
        data = self._poll()
        return data.get('building', False)

    def block_until_complete(self, delay=5):
        assert isinstance(delay, int)
        count = 0
        while self.is_running():
            total_wait = delay * count
            log.info(
                msg="Waited %is for promotion #%s to complete" %
                (total_wait, self.get_number()))
            sleep(delay)
            count += 1
