import os
import time
import shutil
import tempfile
import subprocess


class Timeout(RuntimeError):
    pass


class JenkinsLauncher(object):

    def __init__(self, timeout=10, update_war=False, launch=False):
        self.timeout = timeout
        self.directory = os.path.dirname(__file__)
        if update_war:
            self.update_war()
        if launch:
            self.launch()

    def update_war(self):
        os.chdir(self.directory)
        subprocess.check_call('./get-jenkins-war.sh')

    def launch(self):
        '''
        Launches jenkins and waits while it's ready.
        '''
        self.jenkins_home = tempfile.mkdtemp(prefix='jenkins-home-')
        os.environ['JENKINS_HOME'] = self.jenkins_home
        jenkins_command = 'java -jar jenkins.war'
        self.jenkins_process = subprocess.Popen(
            jenkins_command.split(), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            line = self.jenkins_process.stderr.readline().strip()
            if line == 'INFO: Jenkins is fully up and running':
                return
        raise Timeout('Timeout error occured while waiting for Jenkins start.')

    def stop(self):
        shutil.rmtree(self.jenkins_home)
        self.jenkins_process.terminate()
        self.jenkins_process.wait()


launcher = None


def setUpPackage():
    global launcher
    launcher = JenkinsLauncher(update_war=True, launch=True)


def tearDownPackage():
    launcher.stop()
