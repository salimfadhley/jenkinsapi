#!/bin/sh

JENKINS_WAR_URL="http://mirrors.jenkins-ci.org/war/latest/jenkins.war"

if [ ! -e 'jenkins.war' ]; then
    wget $JENKINS_WAR_URL
fi
