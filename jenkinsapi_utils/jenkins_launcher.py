import os
import time
try:
    import Queue
except ImportError:
    import queue as Queue
import random
import shutil
import logging
import datetime
import tempfile
import posixpath
import requests
import threading
import subprocess
from pkg_resources import resource_stream
from tarfile import TarFile
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import JenkinsAPIException

log = logging.getLogger(__name__)


class FailedToStart(Exception):
    pass


class TimeOut(Exception):
    pass


class StreamThread(threading.Thread):

    def __init__(self, name, q, stream, fn_log):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.stream = stream
        self.fn_log = fn_log

    def run(self):
        log.info("Starting %s", self.name)

        while True:
            line = self.stream.readline()
            if line:
                self.fn_log(line.rstrip())
                self.q.put((self.name, line))
            else:
                break
        self.q.put((self.name, None))


class JenkinsLancher(object):

    """
    Launch jenkins
    """
    JENKINS_WAR_URL = "http://mirrors.jenkins-ci.org/war/latest/jenkins.war"

    def __init__(self, war_path, plugin_urls=None, jenkins_url=None):
        self.jenkins_url = jenkins_url
        self.http_port = random.randint(9000, 10000) if not jenkins_url \
            else urlparse(jenkins_url).port
        self.war_path = war_path
        self.war_directory, self.war_filename = os.path.split(self.war_path)

        if 'JENKINS_HOME' not in os.environ:
            self.jenkins_home = tempfile.mkdtemp(prefix='jenkins-home-')
            os.environ['JENKINS_HOME'] = self.jenkins_home

        self.jenkins_process = None
        self.q = Queue.Queue()
        self.plugin_urls = plugin_urls or []
        if os.environ.get('JENKINS_VERSION', '1.x') == '1.x':
            self.JENKINS_WAR_URL = (
                'http://mirrors.jenkins-ci.org/war-stable/1.651.3/jenkins.war'
            )

    def update_war(self):
        os.chdir(self.war_directory)
        if os.path.exists(self.war_path):
            log.info("We already have the War file...")
        else:
            log.info("Redownloading Jenkins")
            script_dir = os.path.join(self.war_directory,
                                      'get-jenkins-war.sh')
            subprocess.check_call([script_dir,
                                   self.JENKINS_WAR_URL, self.war_directory])

    def update_config(self):
        tarball = TarFile.open(fileobj=resource_stream(
            'jenkinsapi_tests.systests', 'jenkins_home.tar.gz'))
        tarball.extractall(path=self.jenkins_home)

    def install_plugins(self):
        for i, url in enumerate(self.plugin_urls):
            self.install_plugin(url, i)

    def install_plugin(self, hpi_url, i):
        plugin_dir = os.path.join(self.jenkins_home, 'plugins')
        if not os.path.exists(plugin_dir):
            os.mkdir(plugin_dir)

        log.info("Downloading %s", hpi_url)
        log.info("Plugins will be installed in '%s'", plugin_dir)
        path = urlparse(hpi_url).path
        filename = posixpath.basename(path)
        plugin_path = os.path.join(plugin_dir, filename)
        with open(plugin_path, 'wb') as h:
            request = requests.get(hpi_url)
            h.write(request.content)

    def stop(self):
        if not self.jenkins_url:
            log.info("Shutting down jenkins.")
            self.jenkins_process.terminate()
            self.jenkins_process.wait()
            # Do not remove jenkins home if JENKINS_URL is set
            if 'JENKINS_URL' not in os.environ:
                shutil.rmtree(self.jenkins_home)

    def block_until_jenkins_ready(self, timeout):
        start_time = datetime.datetime.now()
        timeout_time = start_time + datetime.timedelta(seconds=timeout)

        while True:
            try:
                Jenkins('http://localhost:8080')
                log.info('Jenkins is finally ready for use.')
            except JenkinsAPIException:
                log.info('Jenkins is not yet ready...')
            if datetime.datetime.now() > timeout_time:
                raise TimeOut('Took too long for Jenkins to become ready...')
            time.sleep(5)

    def start(self, timeout=60):
        if not self.jenkins_url:
            self.jenkins_home = os.environ.get('JENKINS_HOME',
                                               self.jenkins_home)
            self.update_war()
            self.update_config()
            self.install_plugins()

            os.chdir(self.war_directory)

            jenkins_command = ['java',
                               '-Djenkins.install.runSetupWizard=false',
                               '-jar', self.war_filename,
                               '--httpPort=%d' % self.http_port]

            log.info("About to start Jenkins...")
            log.info("%s> %s", os.getcwd(), " ".join(jenkins_command))
            self.jenkins_process = subprocess.Popen(
                jenkins_command, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            threads = [
                StreamThread('out', self.q, self.jenkins_process.stdout,
                             log.info),
                StreamThread('err', self.q, self.jenkins_process.stderr,
                             log.warn)
            ]

            # Start the threads
            for t in threads:
                t.start()

            while True:
                try:
                    streamName, line = self.q.get(block=True, timeout=timeout)
                    # Python 3.x
                    if isinstance(line, bytes):
                        line = line.decode('UTF-8')
                except Queue.Empty:
                    log.warn("Input ended unexpectedly")
                    break
                else:
                    if line:
                        if 'Failed to initialize Jenkins' in line:
                            raise FailedToStart(line)

                        if 'Invalid or corrupt jarfile' in line:
                            raise FailedToStart(line)

                        if 'is fully up and running' in line:
                            log.info(line)
                            return
                    else:
                        log.warn('Stream %s has terminated', streamName)

            self.block_until_jenkins_ready(timeout)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger('').setLevel(logging.INFO)

    log.info("Hello!")

    jl = JenkinsLancher(
        '/home/sal/workspace/jenkinsapi/src/'
        'jenkinsapi_tests/systests/jenkins.war'
    )
    jl.start()
    log.info("Jenkins was launched...")

    time.sleep(30)

    log.info("...now to shut it down!")
    jl.stop()
