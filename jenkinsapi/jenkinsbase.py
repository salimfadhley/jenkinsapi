"""
Module for JenkinsBase class
"""

import ast
import logging
from copy import deepcopy
from jenkinsapi import config
from jenkinsapi.custom_exceptions import JenkinsAPIException


class JenkinsBase(object):
    """
    This appears to be the base object that all other jenkins objects are inherited from
    """
    RETRY_ATTEMPTS = 1

    def __repr__(self):
        return """<%s.%s %s>""" % (self.__class__.__module__,
                                   self.__class__.__name__,
                                   str(self))

    def __str__(self):
        raise NotImplementedError
        
    def __hash__(self):
        #hash is used by some comparative operations
        #jenkins objects should beable to create reliable hashes from their _data member
        def make_hash(o):
            """
            Makes a hash from a dictionary, list, tuple or set to any level, that contains
            only other hashable types (including any lists, tuples, sets, and
            dictionaries).
            """
            if isinstance(o, (set, tuple, list)):
                return tuple([make_hash(e) for e in o])    
            elif not isinstance(o, dict):
                return hash(o)
            
            new_o = deepcopy(o)
            for k, v in new_o.items():
                new_o[k] = make_hash(v)
            
            return hash(tuple(frozenset(sorted(new_o.items()))))
        return make_hash(self._data)

    def __init__(self, baseurl, poll=True):
        """
        Initialize a jenkins connection
        """
        self._data = None
        self.baseurl = self.strip_trailing_slash(baseurl)
        if poll:
            self.poll()

    def get_jenkins_obj(self):
        raise NotImplementedError('Please implement this method on %s' % self.__class__.__name__)

    def __eq__(self, other):
        """
        Return true if the hash of the data they represent matches 
        """
        if isinstance(other, self.__class__):
            return hash(self) == hash(other):
        return False

    @classmethod
    def strip_trailing_slash(cls, url):
        while url.endswith('/'):
            url = url[:-1]
        return url

    def poll(self):
        self._data = self._poll()
        if 'jobs' in self._data:
            self._data['jobs'] = self.resolve_job_folders(self._data['jobs'])

    def _poll(self):
        url = self.python_api_url(self.baseurl)
        return self.get_data(url)

    def get_data(self, url, params=None):
        requester = self.get_jenkins_obj().requester
        response = requester.get_url(url, params)
        if response.status_code != 200:
            response.raise_for_status()
        try:
            return ast.literal_eval(response.text)
        except Exception:
            logging.exception('Inappropriate content found at %s', url)
            raise JenkinsAPIException('Cannot parse %s' % response.content)

    def resolve_job_folders(self, jobs):
        for job in jobs:
            if 'color' not in job.keys():
                jobs.remove(job)
                jobs += self.process_job_folder(job)

        return jobs

    def process_job_folder(self, folder):
        data = self.get_data(self.python_api_url(folder['url']))
        result = []

        for job in data.get('jobs', []):
            if 'color' not in job.keys():
                result += self.process_job_folder(job)
            else:
                result.append(job)

        return result

    @classmethod
    def python_api_url(cls, url):
        if url.endswith(config.JENKINS_API):
            return url
        else:
            if url.endswith(r"/"):
                fmt = "%s%s"
            else:
                fmt = "%s/%s"
            return fmt % (url, config.JENKINS_API)
