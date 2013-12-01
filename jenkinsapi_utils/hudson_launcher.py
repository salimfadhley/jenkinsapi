import os
import time
import Queue
import random
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


class HudsonLancher(object):

    """
    Launch jenkins
    """
    HUDSON_WAR_URL = "http://eclipse.org/downloads/download.php?file=/hudson/war/hudson-3.1.0.war&r=1"

    def __init__(self, war_path, plugin_urls=None):
        self.war_path = war_path
        self.war_directory, self.war_filename = os.path.split(self.war_path)
        self.hudson_home = tempfile.mkdtemp(prefix='hudson-home-')
        self.hudson_process = None
        self.q = Queue.Queue()
        self.plugin_urls = plugin_urls or []
        self.http_port = random.randint(9000, 10000)

    def update_war(self):
        os.chdir(self.war_directory)
        if os.path.exists(self.war_path):
            log.info("We already have the Hudson War file...")
        else:
            log.info("Redownloading Hudson")
            subprocess.check_call('./get-hudson-war.sh')

    def update_config(self):
        config_dest = os.path.join(self.hudson_home, 'config.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.hudsontests', 'config.xml')
        config_dest_file.write(config_source.encode('UTF-8'))

    def update_initsetup(self):
        config_dest = os.path.join(self.hudson_home, 'initSetup.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.hudsontests', 'initSetup.xml')
        config_dest_file.write(config_source.encode('UTF-8'))

    def update_security(self):
        config_dest = os.path.join(self.hudson_home, 'hudson-security.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.hudsontests', 'security.xml')
        config_dest_file.write(config_source.encode('UTF-8'))

    def update_teams(self):

        team_one_dir = os.path.join(self.hudson_home, 'teams/one/jobs')
        if not os.path.exists(team_one_dir):
            os.makedirs(team_one_dir)

        team_two_dir = os.path.join(self.hudson_home, 'teams/two/jobs')
        if not os.path.exists(team_two_dir):
            os.makedirs(team_two_dir)

        config_dest = os.path.join(self.hudson_home, 'teams/teams.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.hudsontests', 'teams.xml')
        config_dest_file.write(config_source.encode('UTF-8'))

    def update_adminuser(self):
        user_dir = os.path.join(self.hudson_home, 'users/admin')
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        config_dest = os.path.join(user_dir, 'config.xml')
        config_dest_file = open(config_dest, 'w')
        config_source = pkg_resources.resource_string('jenkinsapi_tests.hudsontests', 'admin-user.xml')
        config_dest_file.write(config_source.encode('UTF-8'))




    def install_plugins(self):
        for i, url in enumerate(self.plugin_urls):
            self.install_plugin(url, i)

    def install_plugin(self, hpi_url, i):
        plugin_dir = os.path.join(self.hudson_home, 'plugins')
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
        log.info("Shutting down Hudson.")
        self.hudson_process.terminate()
        self.hudson_process.wait()
        shutil.rmtree(self.hudson_home)

    def block_until_hudson_ready(self, timeout, port):
        start_time = datetime.datetime.now()
        timeout_time = start_time + datetime.timedelta(seconds=timeout)

        while True:
            try:
                Jenkins('http://localhost:%s' % port)
                log.info('Hudson is finally ready for use.')
            except JenkinsAPIException:
                log.info('Hudson is not yet ready...')
            if datetime.datetime.now() > timeout_time:
                raise TimeOut('Took too long for Jenkins to become ready...')
            time.sleep(5)

    def start(self, timeout=60):
        self.update_war()
        self.update_config()
        self.update_initsetup()
        self.update_security()
        self.update_teams()
        self.update_adminuser()
        self.install_plugins()

        os.environ['HUDSON_HOME'] = self.hudson_home
        os.chdir(self.war_directory)

        hudson_command = ['java', '-jar', self.war_filename,
            '--httpPort=%d' % self.http_port , "--skipInitSetup"]

        log.info("About to start Hudson...")
        log.info("%s> %s", os.getcwd(), " ".join(hudson_command))
        self.hudson_process = subprocess.Popen(
            hudson_command, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        threads = [
            StreamThread('out', self.q, self.hudson_process.stdout, log.info),
            StreamThread('err', self.q, self.hudson_process.stderr, log.warn)
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
                    if 'Failed to initialize Hudson' in line:
                        raise FailedToStart(line)

                    if 'Invalid or corrupt jarfile' in line:
                        raise FailedToStart(line)

                    if 'Hudson is ready' in line:
                        log.info(line)
                        return
                else:
                    log.warn('Stream %s has terminated', streamName)

        self.block_until_hudson_ready(timeout, self.http_port)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger('').setLevel(logging.INFO)

    log.info("Hello!")

    jl = HudsonLancher(
        '/home/sal/workspace/jenkinsapi/src/jenkinsapi_tests/hudsontests/hudson.war'
    )
    jl.start()
    log.info("Hudson was launched...")

    time.sleep(30)

    log.info("...now to shut it down!")
    jl.stop()
