#!/bin/bash
#JENKINS_WAR_URL="http://mirrors.jenkins-ci.org/war/latest/jenkins.war"

if [[ "$#" -ne 2 ]]; then
    echo "Usage: $0 jenkins_url path_to_store_jenkins"
    exit 1
fi

readonly JENKINS_WAR_URL=$1
readonly JENKINS_PATH=$2

hash wget 2>/dev/null
if [ $? -ne 0 ]; then
    echo "You should install wget to launch tests"
    exit 1
fi

wget -O ${JENKINS_PATH}/jenkins.war $JENKINS_WAR_URL
