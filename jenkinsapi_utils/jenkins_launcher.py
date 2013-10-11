import os
import time
import Queue
import shutil
import logging
import datetime
import tempfile
import requests
import threading
import subprocess
import pkg_resources

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

    def __init__(self, war_path, plugin_urls=None):
        self.war_path = war_path
        self.war_directory, self.war_filename = os.path.split(self.war_path)
        self.jenkins_home = tempfile.mkdtemp(prefix='jenkins-home-')
        self.jenkins_process = None
        self.q = Queue.Queue()
        self.plugin_urls = plugin_urls or []

    def update_war(self):
        os.chdir(self.war_directory)
        if os.path.exists(self.war_path):
            log.info("We already have the War file...")
        else:
            log.info("Redownloading Jenkins")
            subprocess.check_call('./get-jenkins-war.sh')

    def update_config(self):
        config_dest = os.path.join(self.jenkins_home, 'config.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.systests', 'config.xml')
        config_dest_file.write(config_source.encode('UTF-8'))

    def install_plugins(self):
        for i, url in enumerate(self.plugin_urls):
            self.install_plugin(url, i)

    def install_plugin(self, hpi_url, i):
        plugin_dir = os.path.join(self.jenkins_home, 'plugins')
        if not os.path.exists(plugin_dir):
            os.mkdir(plugin_dir)

        log.info("Downloading %s", hpi_url)
        log.info("Plugins will be installed in '%s'" % plugin_dir)
        # FIXME: This is kinda ugly but works
        filename = "plugin_%s.hpi" % i
        plugin_path = os.path.join(plugin_dir, filename)
        with open(plugin_path, 'wb') as h:
            request = requests.get(hpi_url)
            h.write(request.content)

    def stop(self):
        log.info("Shutting down jenkins.")
        self.jenkins_process.terminate()
        self.jenkins_process.wait()
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
        self.update_war()
        self.update_config()
        self.install_plugins()

        os.environ['JENKINS_HOME'] = self.jenkins_home
        os.chdir(self.war_directory)

        jenkins_command = ['java', '-jar', self.war_filename]

        log.info("About to start Jenkins...")
        log.info("%s> %s", os.getcwd(), " ".join(jenkins_command))
        self.jenkins_process = subprocess.Popen(
            jenkins_command, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        threads = [
            StreamThread('out', self.q, self.jenkins_process.stdout, log.info),
            StreamThread('err', self.q, self.jenkins_process.stderr, log.warn)
        ]

        # Start the threads
        for t in threads:
            t.start()

        while True:
            try:
                streamName, line = self.q.get(block=True, timeout=timeout)
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
        '/home/sal/workspace/jenkinsapi/src/jenkinsapi_tests/systests/jenkins.war'
    )
    jl.start()
    log.info("Jenkins was launched...")

    time.sleep(30)

    log.info("...now to shut it down!")
    jl.stop()
